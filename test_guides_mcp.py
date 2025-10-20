#!/usr/bin/env python3
"""
Test client for the Guides MCP Server.

This script demonstrates how to connect to and use the Guides MCP server.

Usage:
  python test_guides_mcp.py
"""

import asyncio
import json
import logging
from typing import Dict, List, Any

from mcp import (
    MCPClient,
    MCPToolSchema,
    MCPClientResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_guides_mcp():
    """Test the Guides MCP server functionality."""
    # Connect to the MCP server
    client = MCPClient(port=8080)
    service_info = await client.get_service_info()
    
    print(f"\n🚀 Connected to MCP service: {service_info.name} v{service_info.version}")
    print(f"Description: {service_info.description}")
    
    # Get available tools
    tools = await client.get_tools()
    print(f"\n🔧 Available Tools ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}: {tool.description}")
    
    # Test 1: List divisions
    print("\n\n📂 Testing list_guide_divisions...")
    divisions_response = await client.call_tool(
        "list_guide_divisions", 
        {}
    )
    
    divisions = divisions_response.result
    print(f"Found {len(divisions)} divisions:")
    for div in divisions:
        print(f"  - {div['name']} ({div['guide_count']} guides)")
    
    if not divisions:
        print("No divisions found. Make sure guides directory exists and has been populated.")
        return
    
    # Test 2: List guides in first division
    test_division = divisions[0]["name"]
    print(f"\n\n📚 Testing list_guides_by_division with '{test_division}'...")
    
    guides_response = await client.call_tool(
        "list_guides_by_division", 
        {"division": test_division}
    )
    
    guides = guides_response.result
    print(f"Found {len(guides)} guides in '{test_division}':")
    for i, guide in enumerate(guides[:5], 1):  # Show first 5 guides only
        print(f"  {i}. {guide['title']} (Maturity: {guide['maturity']})")
    
    if len(guides) > 5:
        print(f"  ... and {len(guides) - 5} more guides")
    
    if not guides:
        print(f"No guides found in '{test_division}'.")
        return
    
    # Test 3: Get guide content for first guide
    test_guide_path = guides[0]["path"]
    print(f"\n\n📄 Testing get_guide_content with '{test_guide_path}'...")
    
    guide_response = await client.call_tool(
        "get_guide_content", 
        {"guide_path": test_guide_path}
    )
    
    guide = guide_response.result
    if "error" in guide:
        print(f"Error: {guide['error']}")
    else:
        print(f"Title: {guide['title']}")
        print(f"Division: {guide['division']}")
        print(f"Maturity: {guide['maturity']}")
        print(f"Content (first 200 chars): {guide['content'][:200]}...")
    
    # Test 4: Search guides
    print("\n\n🔍 Testing search_guides...")
    test_query = "authentication"  # Common term likely to be found
    
    search_response = await client.call_tool(
        "search_guides", 
        {"query": test_query, "top_k": 3}
    )
    
    results = search_response.result
    print(f"Found {len(results)} results for '{test_query}':")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']} ({result['division']})")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Path: {result['file_path']}")
        print(f"   Preview: {result['content_preview'][:100]}...")
    
    # Test 5: Get recommendations
    print("\n\n👉 Testing get_guide_recommendations...")
    
    recommendations_response = await client.call_tool(
        "get_guide_recommendations", 
        {
            "topics": ["authentication", "security"],
            "division": divisions[0]["name"] if divisions else None
        }
    )
    
    recommendations = recommendations_response.result
    print(f"Found {len(recommendations)} recommendations:")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']} ({rec['division']})")
        print(f"   Score: {rec['score']:.3f}")
        print(f"   Path: {rec['file_path']}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_guides_mcp())