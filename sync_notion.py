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
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from notion_client import Client

# --- CONFIGURATION ---
GUIDES_ROOT_DIR = Path("guides")  # The root folder for the guides repository
NOTION_PAGE_SIZE = 100

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

def fetch_block_children(notion: Client, block_id: str, indent_level: int = 0) -> str:
    """Recursively fetches children of a block and converts to markdown."""
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
                children_content = fetch_block_children(notion, block["id"], indent_level + 1)
                if children_content:
                    markdown_lines.append(children_content)
        
        return "\n".join(markdown_lines)
    except Exception as e:
        print(f"  Warning: Could not fetch children for block: {e}")
        return ""

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
        response = notion.databases.query(**query_params)
        pages.extend(response["results"])
        if not response["has_more"]:
            break
        start_cursor = response["next_cursor"]
    print(f"Found {len(pages)} pages in the Notion database.")
    return pages

def process_page(notion: Client, page: dict) -> dict:
    """Processes a single Notion page and writes it to a file."""
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
            children_content = fetch_block_children(notion, block["id"], indent_level=1)
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
            print(f"  Skipped (unchanged): {file_path}")
            return {"division": division, "title": clean_title, "path": f"./{division_slug}/{title_slug}/", "file_path": str(file_path)}
        else:
            action = "updated"
    
    # --- Write the File ---
    file_path.write_text(new_content, encoding="utf-8")
    print(f"  {action.capitalize()}: {file_path}")
    
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
    print("Starting Notion to Git sync...")
    load_dotenv()
    
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    notion_view_id = os.getenv("NOTION_VIEW_ID", "1aea172b65a3801e8f5b000c48917d78")  # Default to "All" view

    if not notion_api_key or not notion_database_id:
        print("Error: NOTION_API_KEY and NOTION_DATABASE_ID must be set in .env file.")
        return

    # Ensure guides directory exists
    if not GUIDES_ROOT_DIR.exists():
        GUIDES_ROOT_DIR.mkdir()

    notion = Client(auth=notion_api_key)
    pages = fetch_all_database_pages(notion, notion_database_id, notion_view_id)
    
    # Track all synced files
    synced_files = set()
    processed_pages = []
    
    for page in pages:
        result = process_page(notion, page)
        processed_pages.append(result)
        synced_files.add(result["file_path"])
    
    # Delete files that are no longer in Notion
    print("\nCleaning up removed pages...")
    deleted_count = 0
    if GUIDES_ROOT_DIR.exists():
        for module_dir in GUIDES_ROOT_DIR.iterdir():
            if module_dir.is_dir() and module_dir.name != "README.md":
                for guide_dir in module_dir.iterdir():
                    if guide_dir.is_dir():
                        index_file = guide_dir / "index.md"
                        if index_file.exists() and str(index_file) not in synced_files:
                            print(f"  Deleted: {index_file}")
                            shutil.rmtree(guide_dir)
                            deleted_count += 1
                # Remove empty module directories
                if not any(module_dir.iterdir()):
                    shutil.rmtree(module_dir)
    
    if deleted_count > 0:
        print(f"Removed {deleted_count} obsolete page(s)")
        
    generate_master_catalog(processed_pages)
    
    print("\nSync complete!")

if __name__ == "__main__":
    main()
