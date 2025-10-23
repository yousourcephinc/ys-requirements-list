#!/usr/bin/env python3
"""Sync Notion database pages into a local guides/ folder as Markdown files.

Usage:
  - Create a `.env` file with NOTION_API_KEY and NOTION_DATABASE_ID
  - pip install -r requirements.txt
  - python sync_notion.py
"""

import os
import re
import shutil
import json
import time
from collections import defaultdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from dotenv import load_dotenv
from notion_client import Client

# --- CONFIGURATION ---
GUIDES_ROOT_DIR = Path("guides")  # The root folder for the guides repository
NOTION_PAGE_SIZE = 100
MAX_WORKERS = 5  # Number of parallel workers for fetching content
RATE_LIMIT_DELAY = 0.3  # Delay between requests in seconds (Notion allows ~3 requests/sec)

# --- HELPER FUNCTIONS ---

def slugify(text: str) -> str:
    """Converts a string to a filesystem-friendly 'slug'."""
    text = text.lower()
    text = re.sub(r"\s+", "-", text)  # Replace spaces with hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)  # Remove non-alphanumeric characters
    return text

def parse_page_title(title: str) -> str:
    """Removes division prefix from title if present."""
    # Remove common division prefixes (PM, QA, SE, etc.)
    parts = title.split(" - ", 1)
    if len(parts) == 2 and parts[0].strip().upper() in ["PM", "QA", "SE"]:
        return parts[1].strip()
    return title.strip()

def notion_rich_text_to_markdown(rich_text_list: list) -> str:
    """Converts a Notion rich_text list to a Markdown string."""
    markdown_text = ""
    for rich_text in rich_text_list:
        content = rich_text.get("plain_text", "")
        annotations = rich_text.get("annotations", {})
        if annotations.get("bold"):
            content = f"**{content}**"
        if annotations.get("italic"):
            content = f"*{content}*"
        if annotations.get("code"):
            content = f"`{content}`"
        markdown_text += content
    return markdown_text

def notion_blocks_to_markdown(blocks: list) -> str:
    """Converts a list of Notion blocks to a Markdown string."""
    markdown_lines = []
    for block in blocks:
        block_type = block["type"]
        if block_type == "heading_1":
            text = notion_rich_text_to_markdown(block["heading_1"]["rich_text"])
            markdown_lines.append(f"# {text}")
        elif block_type == "heading_2":
            text = notion_rich_text_to_markdown(block["heading_2"]["rich_text"])
            markdown_lines.append(f"## {text}")
        elif block_type == "heading_3":
            text = notion_rich_text_to_markdown(block["heading_3"]["rich_text"])
            markdown_lines.append(f"### {text}")
        elif block_type == "paragraph":
            text = notion_rich_text_to_markdown(block["paragraph"]["rich_text"])
            markdown_lines.append(text if text else "")
        elif block_type == "bulleted_list_item":
            text = notion_rich_text_to_markdown(block["bulleted_list_item"]["rich_text"])
            markdown_lines.append(f"- {text}")
        elif block_type == "numbered_list_item":
            text = notion_rich_text_to_markdown(block["numbered_list_item"]["rich_text"])
            markdown_lines.append(f"1. {text}")
        elif block_type == "code":
            lang = block["code"].get("language") or ""
            text = notion_rich_text_to_markdown(block["code"]["rich_text"])
            markdown_lines.append(f"```{lang}\n{text}\n```")
        elif block_type == "to_do":  # Handle checklists
            text = notion_rich_text_to_markdown(block["to_do"]["rich_text"])
            checked = block["to_do"].get("checked")
            markdown_lines.append(f"- [{'x' if checked else ' '}] {text}")

    return "\n".join(markdown_lines)

def fetch_block_children(notion: Client, block_id: str, indent_level: int = 0, rate_limiter: Lock = None) -> str:
    """Recursively fetches children of a block and converts to markdown."""
    # Rate limiting
    if rate_limiter:
        with rate_limiter:
            time.sleep(RATE_LIMIT_DELAY)
    
    try:
        children_response = notion.blocks.children.list(block_id=block_id)
        children_blocks = children_response.get("results", [])
        if not children_blocks:
            return ""
        
        markdown_lines = []
        indent = "  " * indent_level
        
        for block in children_blocks:
            block_type = block["type"]
            
            if block_type == "heading_1":
                text = notion_rich_text_to_markdown(block["heading_1"]["rich_text"])
                markdown_lines.append(f"# {text}")
            elif block_type == "heading_2":
                text = notion_rich_text_to_markdown(block["heading_2"]["rich_text"])
                markdown_lines.append(f"## {text}")
            elif block_type == "heading_3":
                text = notion_rich_text_to_markdown(block["heading_3"]["rich_text"])
                markdown_lines.append(f"### {text}")
            elif block_type == "paragraph":
                text = notion_rich_text_to_markdown(block["paragraph"]["rich_text"])
                markdown_lines.append(indent + text if text else "")
            elif block_type == "bulleted_list_item":
                text = notion_rich_text_to_markdown(block["bulleted_list_item"]["rich_text"])
                markdown_lines.append(f"{indent}- {text}")
            elif block_type == "numbered_list_item":
                text = notion_rich_text_to_markdown(block["numbered_list_item"]["rich_text"])
                markdown_lines.append(f"{indent}1. {text}")
            elif block_type == "code":
                lang = block["code"].get("language") or ""
                text = notion_rich_text_to_markdown(block["code"]["rich_text"])
                markdown_lines.append(f"{indent}```{lang}\n{text}\n```")
            elif block_type == "to_do":
                text = notion_rich_text_to_markdown(block["to_do"]["rich_text"])
                checked = block["to_do"].get("checked")
                markdown_lines.append(f"{indent}- [{'x' if checked else ' '}] {text}")
            elif block_type == "toggle":
                text = notion_rich_text_to_markdown(block["toggle"]["rich_text"])
                markdown_lines.append(f"\n{indent}**{text}**\n")
            
            # Recursively fetch children if block has them
            if block.get("has_children"):
                children_content = fetch_block_children(notion, block["id"], indent_level + 1, rate_limiter)
                if children_content:
                    markdown_lines.append(children_content)
        
        return "\n".join(markdown_lines)
    except Exception as e:
        print(f"  Warning: Could not fetch children for block: {e}")
        return ""

# --- SEMANTIC SEARCH FUNCTIONS ---
# Note: Semantic search has been moved to vector_search.py using Vertex AI
# These functions are kept for backward compatibility but are no longer called

# --- CORE LOGIC ---

def fetch_all_database_pages(notion: Client, database_id: str, view_id: str = None) -> list:
    """Fetches all pages from a Notion database, handling pagination."""
    pages = []
    start_cursor = None
    
    # Build query parameters
    query_params = {
        "database_id": database_id,
        "page_size": NOTION_PAGE_SIZE,
    }
    
    # Add filter_properties if view_id is provided
    if view_id:
        query_params["filter_properties"] = [view_id]
    
    while True:
        query_params["start_cursor"] = start_cursor
        print(f"  📥 Fetching batch (cursor: {start_cursor[:20] if start_cursor else 'initial'}...)")
        response = notion.databases.query(**query_params)
        batch_size = len(response["results"])
        pages.extend(response["results"])
        print(f"  ✓ Retrieved {batch_size} pages (total: {len(pages)})")
        if not response["has_more"]:
            break
        start_cursor = response["next_cursor"]
    print(f"✅ Found {len(pages)} pages in the Notion database.")
    return pages

def process_page(notion: Client, page: dict, rate_limiter: Lock = None) -> dict:
    """Processes a single Notion page and writes it to a file."""
    # Rate limiting
    if rate_limiter:
        with rate_limiter:
            time.sleep(RATE_LIMIT_DELAY)
    
    properties = page.get("properties", {})
    title = properties.get("Name", {}).get("title", [{}])[0].get("plain_text", "Untitled")
    
    # Get division from property
    division_prop = properties.get("Division", {}).get("select")
    division = division_prop.get("name") if division_prop else "uncategorized"
    
    # Remove division prefix from title
    clean_title = parse_page_title(title)
    
    # Create slugs
    division_slug = slugify(division)
    title_slug = slugify(clean_title)

    # Create directory structure: guides/{division}/{title}/
    guide_dir = GUIDES_ROOT_DIR / division_slug / title_slug
    guide_dir.mkdir(parents=True, exist_ok=True)
    
    # --- Generate YAML Frontmatter ---
    frontmatter = ["---"]
    frontmatter.append(f'title: "{clean_title}"')
    frontmatter.append(f'division: "{division}"')
    
    # Extract other properties
    maturity_prop = properties.get("Maturity Level", {}).get("select")
    if maturity_prop:
        maturity = maturity_prop.get("name")
        if maturity:
            frontmatter.append(f"maturity: \"{maturity}\"")

    frontmatter.append(f'source_url: {page.get("url")}')
    frontmatter.append("---")
    
    # --- Fetch and Convert Page Content ---
    # Fetch blocks with nested children support
    markdown_lines = []
    page_blocks = notion.blocks.children.list(block_id=page["id"])["results"]
    
    for block in page_blocks:
        block_type = block["type"]
        
        if block_type == "heading_1":
            text = notion_rich_text_to_markdown(block["heading_1"]["rich_text"])
            markdown_lines.append(f"# {text}")
        elif block_type == "heading_2":
            text = notion_rich_text_to_markdown(block["heading_2"]["rich_text"])
            markdown_lines.append(f"## {text}")
        elif block_type == "heading_3":
            text = notion_rich_text_to_markdown(block["heading_3"]["rich_text"])
            markdown_lines.append(f"### {text}")
        elif block_type == "paragraph":
            text = notion_rich_text_to_markdown(block["paragraph"]["rich_text"])
            markdown_lines.append(text if text else "")
        elif block_type == "bulleted_list_item":
            text = notion_rich_text_to_markdown(block["bulleted_list_item"]["rich_text"])
            markdown_lines.append(f"- {text}")
        elif block_type == "numbered_list_item":
            text = notion_rich_text_to_markdown(block["numbered_list_item"]["rich_text"])
            markdown_lines.append(f"1. {text}")
        elif block_type == "code":
            lang = block["code"].get("language") or ""
            text = notion_rich_text_to_markdown(block["code"]["rich_text"])
            markdown_lines.append(f"```{lang}\n{text}\n```")
        elif block_type == "to_do":
            text = notion_rich_text_to_markdown(block["to_do"]["rich_text"])
            checked = block["to_do"].get("checked")
            markdown_lines.append(f"- [{'x' if checked else ' '}] {text}")
        elif block_type == "toggle":
            text = notion_rich_text_to_markdown(block["toggle"]["rich_text"])
            markdown_lines.append(f"\n**{text}**\n")
        
        # Fetch children if block has them
        if block.get("has_children"):
            children_content = fetch_block_children(notion, block["id"], indent_level=1, rate_limiter=rate_limiter)
            if children_content:
                markdown_lines.append(children_content)
    
    markdown_content = "\n".join(markdown_lines)
    
    # --- Generate new content ---
    new_content = "\n".join(frontmatter) + "\n\n" + markdown_content
    
    # --- Check if file exists and compare content ---
    file_path = guide_dir / "index.md"
    action = "created"
    
    if file_path.exists():
        existing_content = file_path.read_text(encoding="utf-8")
        if existing_content == new_content:
            print(f"  ⏭️  Skipped (unchanged): {division}/{clean_title}")
            return {"division": division, "title": clean_title, "path": f"./{division_slug}/{title_slug}/", "file_path": str(file_path)}
        else:
            action = "updated"
    
    # --- Write the File ---
    file_path.write_text(new_content, encoding="utf-8")
    print(f"  {('✨' if action == 'created' else '📝')} {action.capitalize()}: {division}/{clean_title}")
    
    return {"division": division, "title": clean_title, "path": f"./{division_slug}/{title_slug}/", "file_path": str(file_path)}

def generate_master_catalog(processed_pages: list):
    """Generates the main README.md catalog file."""
    catalog = defaultdict(list)
    for page in processed_pages:
        catalog[page["division"]].append(page)
        
    readme_lines = ["# Implementation Guides Catalog", ""]
    readme_lines.append("This repository contains the official, curated implementation guides for all engineering teams, synced from Notion.")
    
    for division, guides in sorted(catalog.items()):
        readme_lines.append(f"\n## {division}\n")
        for guide in sorted(guides, key=lambda x: x['title']):
            readme_lines.append(f"- **[{guide['title']}]({guide['path']})**")
            
    readme_path = GUIDES_ROOT_DIR / "README.md"
    readme_path.write_text("\n".join(readme_lines), encoding="utf-8")
    print(f"\nGenerated master catalog: {readme_path}")

def main():
    """Main function to run the sync process."""
    print("\n🚀 Starting Notion to Git sync...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    load_dotenv()
    
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    notion_view_id = os.getenv("NOTION_VIEW_ID", "1aea172b65a3801e8f5b000c48917d78")  # Default to "All" view

    if not notion_api_key or not notion_database_id:
        print("❌ Error: NOTION_API_KEY and NOTION_DATABASE_ID must be set in .env file.")
        return

    print("\n✅ Environment variables loaded:")
    print(f"   Database ID: {notion_database_id}")
    print(f"   View ID: {notion_view_id}")
    print(f"   API Key: {notion_api_key[:15]}...")

    # Ensure guides directory exists
    if not GUIDES_ROOT_DIR.exists():
        GUIDES_ROOT_DIR.mkdir()
        print(f"\n📁 Created guides directory: {GUIDES_ROOT_DIR.absolute()}")
    else:
        print(f"\n📂 Using guides directory: {GUIDES_ROOT_DIR.absolute()}")

    print("\n🔗 Connecting to Notion API...")
    notion = Client(auth=notion_api_key)
    print("✅ Connected successfully\n")
    
    print("📋 Fetching database pages...")
    pages = fetch_all_database_pages(notion, notion_database_id, notion_view_id)
    
    # Track all synced files
    synced_files = set()
    processed_pages = []
    rate_limiter = Lock()
    
    print(f"\n📝 Processing {len(pages)} pages in parallel (max {MAX_WORKERS} workers)...\n")
    
    # Process pages in parallel with progress tracking
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_page = {
            executor.submit(process_page, notion, page, rate_limiter): (i, page) 
            for i, page in enumerate(pages, 1)
        }
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_page):
            i, page = future_to_page[future]
            try:
                print(f"[{i}/{len(pages)}]", end=" ")
                result = future.result()
                processed_pages.append(result)
                synced_files.add(result["file_path"])
            except Exception as e:
                page_title = page.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("plain_text", "Unknown")
                print(f"\n❌ Error processing page '{page_title}': {e}")
    
    # Delete files that are no longer in Notion
    print("\n\n🧹 Cleaning up removed pages...")
    deleted_count = 0
    if GUIDES_ROOT_DIR.exists():
        for module_dir in GUIDES_ROOT_DIR.iterdir():
            if module_dir.is_dir() and module_dir.name != "README.md":
                for guide_dir in module_dir.iterdir():
                    if guide_dir.is_dir():
                        index_file = guide_dir / "index.md"
                        if index_file.exists() and str(index_file) not in synced_files:
                            print(f"  🗑️  Deleted: {index_file}")
                            shutil.rmtree(guide_dir)
                            deleted_count += 1
                # Remove empty module directories
                if not any(module_dir.iterdir()):
                    print(f"  📁 Removed empty directory: {module_dir.name}")
                    shutil.rmtree(module_dir)
    
    if deleted_count > 0:
        print(f"✅ Removed {deleted_count} obsolete page(s)")
    else:
        print("✅ No obsolete pages to remove")
    
    print("\n📚 Generating master catalog...")
    generate_master_catalog(processed_pages)
    
    print("\n" + "="*60)
    print("✅ Sync complete!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   • Total pages processed: {len(processed_pages)}")
    print(f"   • Files synced: {len(synced_files)}")
    print(f"   • Obsolete files removed: {deleted_count}")
    
    # Count by division
    division_counts = defaultdict(int)
    for page in processed_pages:
        division_counts[page['division']] += 1
    
    print(f"\n📂 By Division:")
    for division in sorted(division_counts.keys()):
        print(f"   • {division}: {division_counts[division]} guides")
    print()

if __name__ == "__main__":
    main()
