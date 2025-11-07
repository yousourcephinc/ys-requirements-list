#!/usr/bin/env python3
"""
Upload local foundational guides to Notion database.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
import frontmatter

# Load environment variables
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GUIDES_ROOT = Path("guides")

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9-]", "", text)
    return text

def parse_guide(guide_path: Path):
    """Parse a guide markdown file and extract metadata."""
    with open(guide_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    return {
        'title': post.get('title', ''),
        'division': post.get('division', 'se'),
        'maturity': post.get('maturity', 'foundational-1'),
        'content': post.content,
        'frontmatter': post.metadata
    }

def markdown_to_notion_blocks(content: str, max_blocks=100):
    """Convert markdown content to Notion blocks (simplified version)."""
    blocks = []
    lines = content.split('\n')
    
    current_paragraph = []
    
    for line in lines:
        # Skip empty lines between paragraphs
        if not line.strip():
            if current_paragraph:
                # Flush current paragraph
                text = ' '.join(current_paragraph)
                if len(text) <= 2000:  # Notion text limit
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": text[:2000]}
                            }]
                        }
                    })
                current_paragraph = []
            continue
        
        # Heading 1
        if line.startswith('# '):
            if current_paragraph:
                text = ' '.join(current_paragraph)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": text[:2000]}
                        }]
                    }
                })
                current_paragraph = []
            
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": line[2:].strip()[:2000]}
                    }]
                }
            })
        
        # Heading 2
        elif line.startswith('## '):
            if current_paragraph:
                text = ' '.join(current_paragraph)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": text[:2000]}
                        }]
                    }
                })
                current_paragraph = []
            
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": line[3:].strip()[:2000]}
                    }]
                }
            })
        
        # Heading 3
        elif line.startswith('### '):
            if current_paragraph:
                text = ' '.join(current_paragraph)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": text[:2000]}
                        }]
                    }
                })
                current_paragraph = []
            
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": line[4:].strip()[:2000]}
                    }]
                }
            })
        
        # Bullet list
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            if current_paragraph:
                text = ' '.join(current_paragraph)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": text[:2000]}
                        }]
                    }
                })
                current_paragraph = []
            
            bullet_text = re.sub(r'^[\s\-\*]+', '', line).strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": bullet_text[:2000]}
                    }]
                }
            })
        
        # Regular paragraph line
        else:
            current_paragraph.append(line.strip())
        
        # Stop if we hit the max blocks
        if len(blocks) >= max_blocks:
            break
    
    # Flush any remaining paragraph
    if current_paragraph and len(blocks) < max_blocks:
        text = ' '.join(current_paragraph)
        if len(text.strip()) > 0:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": text[:2000]}
                    }]
                }
            })
    
    return blocks[:max_blocks]

def upload_guide_to_notion(client: Client, guide_data: dict, database_id: str):
    """Upload a single guide to Notion."""
    title = guide_data['title']
    division = guide_data['division'].upper()
    maturity = guide_data['maturity']
    
    # Format maturity level for Notion (capitalize first letter of each word)
    maturity_formatted = maturity.replace('-', ' ').title()
    
    print(f"\n📤 Uploading: {title}")
    print(f"   Division: {division}, Maturity: {maturity_formatted}")
    
    # Create the page properties
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": f"{division} - {title}"
                    }
                }
            ]
        },
        "Division": {
            "select": {
                "name": division
            }
        },
        "Maturity Level": {
            "select": {
                "name": maturity_formatted
            }
        }
    }
    
    # Convert content to Notion blocks
    children = markdown_to_notion_blocks(guide_data['content'], max_blocks=100)
    
    try:
        # Create the page
        response = client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=children
        )
        
        page_url = response.get('url', 'N/A')
        print(f"   ✅ Created: {page_url}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main function to upload all foundational guides."""
    print("🚀 Starting upload of foundational guides to Notion...")
    
    # Initialize Notion client
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("❌ Error: NOTION_API_KEY or NOTION_DATABASE_ID not set in .env")
        return
    
    client = Client(auth=NOTION_API_KEY)
    
    # Find all foundational guides
    foundational_guides = list(GUIDES_ROOT.glob("se/*foundational-1*/index.md"))
    
    print(f"\n📊 Found {len(foundational_guides)} foundational guides")
    
    success_count = 0
    error_count = 0
    
    for guide_path in foundational_guides:
        try:
            guide_data = parse_guide(guide_path)
            
            # Skip if no title
            if not guide_data['title']:
                print(f"\n⚠️  Skipping {guide_path.parent.name} (no title)")
                continue
            
            if upload_guide_to_notion(client, guide_data, NOTION_DATABASE_ID):
                success_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            print(f"\n❌ Error processing {guide_path}: {e}")
            error_count += 1
    
    print(f"\n✨ Upload complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Errors: {error_count}")

if __name__ == "__main__":
    main()
