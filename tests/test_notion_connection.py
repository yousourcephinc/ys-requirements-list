#!/usr/bin/env python3
"""Test script to verify Notion API connectivity and grab one page from the database.

Usage:
  python test_notion_connection.py
"""

import os
import json
from dotenv import load_dotenv
from notion_client import Client

def test_notion_connection():
    """Test Notion API connectivity and fetch one page."""
    print("🔍 Testing Notion API connectivity...")
    
    # Load environment variables
    load_dotenv()
    
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_api_key or not notion_database_id:
        print("❌ Error: NOTION_API_KEY and NOTION_DATABASE_ID must be set in .env file.")
        return False
        
    print(f"✅ Environment variables loaded")
    print(f"   Database ID: {notion_database_id}")
    print(f"   API Key: {notion_api_key[:15]}...")
    
    try:
        # Initialize Notion client
        notion = Client(auth=notion_api_key)
        print("✅ Notion client initialized")
        
        # Test database access by querying for just 1 page
        print(f"🔗 Querying database for 1 page...")
        response = notion.databases.query(
            database_id=notion_database_id,
            page_size=1
        )
        
        pages = response.get("results", [])
        
        if not pages:
            print("⚠️  Database is empty or no accessible pages found")
            return True
            
        print(f"✅ Successfully retrieved {len(pages)} page(s)")
        
        # Display information about the first page
        page = pages[0]
        page_id = page.get("id")
        page_url = page.get("url")
        
        print(f"\n📄 Page Details:")
        print(f"   Page ID: {page_id}")
        print(f"   Page URL: {page_url}")
        
        # Extract title from properties
        properties = page.get("properties", {})
        title_property = properties.get("Name", {})
        title_list = title_property.get("title", [])
        title = title_list[0].get("plain_text", "Untitled") if title_list else "Untitled"
        
        print(f"   Title: {title}")
        
        # Show all available properties
        print(f"\n📋 Available Properties:")
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type", "unknown")
            print(f"   - {prop_name}: {prop_type}")
            
        # Test fetching page content
        print(f"\n📝 Testing page content retrieval...")
        blocks_response = notion.blocks.children.list(block_id=page_id, page_size=5)
        blocks = blocks_response.get("results", [])
        
        print(f"✅ Retrieved {len(blocks)} content blocks")
        
        if blocks:
            print(f"\n🧱 First few blocks:")
            for i, block in enumerate(blocks[:3], 1):
                block_type = block.get("type", "unknown")
                print(f"   {i}. {block_type}")
        
        print(f"\n🎉 Connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Notion connection: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_notion_connection()
    exit(0 if success else 1)