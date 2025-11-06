#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Guides

This script creates an MCP server that exposes tools to interact with the guides.

Usage:
  python guides_mcp.py
"""

import asyncio
import json
import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

from mcp import (
    generate_mcp_completion,
    setup_mcp_server,
    tool,
    MessageDict,
    MCPCompletionRequest,
    MCPCompletionResponse,
    MCPServiceInfo,
    MCPTool,
    JsonSchemaProperty,
    JsonSchema,
    MCPSchemaRegistry,
)

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import guide-related functions from scripts
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import from sync_notion for guide directory constant
try:
    from sync_notion import GUIDES_ROOT_DIR
except ImportError:
    GUIDES_ROOT_DIR = Path("guides")

# Import search functionality from vector_search
try:
    from vector_search import search_guides as vector_search_guides, build_index_from_guides
except ImportError:
    logger.warning("Could not import vector_search. Search functionality will be limited.")
    vector_search_guides = None
    build_index_from_guides = None

# Service information
SERVICE_INFO = MCPServiceInfo(
    name="guides_mcp",
    description="MCP service providing tools to interact with implementation guides",
    version="0.1.0",
)

# --- Tool Implementations ---

@tool
async def list_guide_divisions() -> List[Dict[str, Any]]:
    """
    List all divisions (categories) of guides in the repository.
    
    Returns:
        A list of divisions with their name and guide count.
    """
    divisions = []
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    if not guides_dir.exists():
        return divisions
    
    for division_dir in guides_dir.iterdir():
        if division_dir.is_dir() and division_dir.name not in ("semantic_index", "README.md"):
            guide_count = 0
            for _ in division_dir.iterdir():
                if _.is_dir():
                    guide_count += 1
                    
            divisions.append({
                "name": division_dir.name,
                "guide_count": guide_count
            })
    
    return sorted(divisions, key=lambda x: x["name"])


@tool
async def list_guides_by_division(division: str) -> List[Dict[str, Any]]:
    """
    List all guides in a specific division.
    
    Args:
        division: The division (category) name to list guides from
        
    Returns:
        A list of guides in the specified division.
    """
    guides = []
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    division_dir = guides_dir / division
    
    if not division_dir.exists() or not division_dir.is_dir():
        return guides
    
    for guide_dir in division_dir.iterdir():
        if guide_dir.is_dir():
            index_file = guide_dir / "index.md"
            if index_file.exists():
                # Extract title from frontmatter
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = "Unknown"
                maturity = "Unknown"
                
                # Extract metadata from frontmatter
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('title:'):
                        title = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('maturity:'):
                        maturity = line.split(':', 1)[1].strip().strip('"')
                
                guides.append({
                    "slug": guide_dir.name,
                    "title": title,
                    "maturity": maturity,
                    "path": str(index_file.relative_to(guides_dir))
                })
    
    return sorted(guides, key=lambda x: x["title"])


@tool
async def get_guide_content(guide_path: str) -> Dict[str, Any]:
    """
    Get the content of a specific guide.
    
    Args:
        guide_path: Relative path to the guide index file (e.g., "pm/user-management/index.md")
        
    Returns:
        Dictionary with guide content and metadata
    """
    guides_dir = Path(GUIDES_ROOT_DIR)
    guide_file = guides_dir / guide_path
    
    if not guide_file.exists():
        return {
            "error": "Guide not found",
            "guide_path": guide_path
        }
    
    try:
        with open(guide_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse frontmatter and content
        frontmatter = {}
        markdown_content = content
        
        if content.startswith('---'):
            _, frontmatter_content, markdown_content = content.split('---', 2)
            
            # Parse frontmatter
            for line in frontmatter_content.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"')
        
        return {
            "title": frontmatter.get("title", "Untitled"),
            "division": frontmatter.get("division", "Unknown"),
            "maturity": frontmatter.get("maturity", "Unknown"),
            "source_url": frontmatter.get("source_url", ""),
            "content": markdown_content.strip(),
            "path": guide_path
        }
    except Exception as e:
        logger.error(f"Error reading guide: {str(e)}")
        return {
            "error": f"Error reading guide: {str(e)}",
            "guide_path": guide_path
        }


@tool
async def search_guides(
    query: str, 
    top_k: int = 5,
    maturity_filter: Optional[str] = None,
    include_foundational: bool = True
) -> List[Dict[str, Any]]:
    """
    Search guides using semantic search with optional maturity filtering.
    
    Args:
        query: The search query
        top_k: Maximum number of results to return (default: 5)
        maturity_filter: Filter by maturity level (e.g., 'introduction-1', 'growth-1')
        include_foundational: Whether to always include foundational guides (default: True)
        
    Returns:
        A list of matching guide results
    """
    if vector_search_guides is None:
        return []
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    
    # Check if index exists, if not build it
    # Note: For Firestore-based search, the index is maintained via the sync workflow
    # This check is primarily for local development
    try:
        results = vector_search_guides(
            query, 
            top_k=top_k,
            maturity_filter=maturity_filter,
            include_foundational=include_foundational
        )
    except Exception as e:
        logger.error(f"Error searching guides: {e}")
        return []
    
    # Convert to expected return format
    formatted_results = []
    for result in results:
        formatted_results.append({
            "title": result["title"],
            "division": result["division"],
            "file_path": result["file_path"],
            "score": result["score"],
            "content_preview": result["content_preview"]
        })
    
    return formatted_results


@tool
async def rebuild_semantic_index() -> Dict[str, Any]:
    """
    Rebuild the semantic search index for guides.
    
    Returns:
        Status of the indexing operation
    """
    if build_index_from_guides is None:
        return {
            "success": False,
            "error": "Index building functionality not available"
        }
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    
    try:
        logger.info("Rebuilding semantic search index...")
        result = build_index_from_guides(guides_dir)
        return result
    except Exception as e:
        logger.error(f"Error rebuilding semantic index: {str(e)}")
        return {
            "success": False,
            "error": f"Error rebuilding semantic index: {str(e)}"
        }


@tool
async def get_guide_recommendations(
    topics: List[str], 
    maturity_level: Optional[str] = None, 
    division: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get guide recommendations based on topics and filters.
    
    Args:
        topics: List of topics of interest
        maturity_level: Filter by maturity level (optional)
        division: Filter by division (optional)
        
    Returns:
        A list of recommended guides
    """
    if vector_search_guides is None:
        return []
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    
    # Build combined query from topics
    query = " ".join(topics)
    
    # Get initial results from semantic search with maturity filtering
    try:
        results = vector_search_guides(
            query, 
            top_k=10,
            division_filter=division,
            maturity_filter=maturity_level,
            include_foundational=True
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return []
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "title": result["title"],
            "division": result["division"],
            "file_path": result["file_path"],
            "score": result["score"],
            "content_preview": result["content_preview"]
        })
    
    # Return top 5 recommendations
    return formatted_results[:5]
    # Return top 5 after filtering
    return filtered_results[:5]


# --- Schema Registry and Server Setup ---

def register_schemas() -> MCPSchemaRegistry:
    """Register all schemas for the MCP server."""
    registry = MCPSchemaRegistry()
    
    # Define schema for guide division list
    registry.register_schema(
        "ListGuideDivisionsResult",
        JsonSchema(
            type="array",
            items=JsonSchema(
                type="object",
                properties={
                    "name": JsonSchemaProperty("string", "Name of the division"),
                    "guide_count": JsonSchemaProperty("integer", "Number of guides in the division")
                }
            )
        )
    )
    
    # Define schema for guide list
    registry.register_schema(
        "ListGuidesByDivisionResult",
        JsonSchema(
            type="array",
            items=JsonSchema(
                type="object",
                properties={
                    "slug": JsonSchemaProperty("string", "URL slug of the guide"),
                    "title": JsonSchemaProperty("string", "Title of the guide"),
                    "maturity": JsonSchemaProperty("string", "Maturity level of the guide"),
                    "path": JsonSchemaProperty("string", "Path to the guide file")
                }
            )
        )
    )
    
    # Define schema for guide content
    registry.register_schema(
        "GetGuideContentResult",
        JsonSchema(
            type="object",
            properties={
                "title": JsonSchemaProperty("string", "Title of the guide"),
                "division": JsonSchemaProperty("string", "Division of the guide"),
                "maturity": JsonSchemaProperty("string", "Maturity level of the guide"),
                "source_url": JsonSchemaProperty("string", "URL to the source Notion page"),
                "content": JsonSchemaProperty("string", "Markdown content of the guide"),
                "path": JsonSchemaProperty("string", "Path to the guide file"),
                "error": JsonSchemaProperty("string", "Error message if guide not found", required=False)
            }
        )
    )
    
    # Define schema for search results
    registry.register_schema(
        "SearchGuidesResult",
        JsonSchema(
            type="array",
            items=JsonSchema(
                type="object",
                properties={
                    "title": JsonSchemaProperty("string", "Title of the guide"),
                    "division": JsonSchemaProperty("string", "Division of the guide"),
                    "file_path": JsonSchemaProperty("string", "Path to the guide file"),
                    "score": JsonSchemaProperty("number", "Search relevance score"),
                    "content_preview": JsonSchemaProperty("string", "Preview snippet from the guide content")
                }
            )
        )
    )
    
    # Define schema for index rebuild status
    registry.register_schema(
        "RebuildIndexResult",
        JsonSchema(
            type="object",
            properties={
                "success": JsonSchemaProperty("boolean", "Whether the operation was successful"),
                "message": JsonSchemaProperty("string", "Success message", required=False),
                "error": JsonSchemaProperty("string", "Error message", required=False)
            }
        )
    )
    
    return registry


async def main():
    """Main entry point for the MCP server."""
    # Register all schemas
    schema_registry = register_schemas()
    
    # Define tools
    tools = [
        MCPTool(
            function=list_guide_divisions,
            description="List all divisions (categories) of implementation guides",
            output_schema=schema_registry.get_schema("ListGuideDivisionsResult"),
        ),
        MCPTool(
            function=list_guides_by_division,
            description="List all guides in a specific division",
            parameters=JsonSchema(
                type="object",
                properties={
                    "division": JsonSchemaProperty(
                        "string",
                        "The division (category) name to list guides from",
                        required=True
                    )
                }
            ),
            output_schema=schema_registry.get_schema("ListGuidesByDivisionResult"),
        ),
        MCPTool(
            function=get_guide_content,
            description="Get the content of a specific guide",
            parameters=JsonSchema(
                type="object",
                properties={
                    "guide_path": JsonSchemaProperty(
                        "string",
                        "Relative path to the guide index file",
                        required=True
                    )
                }
            ),
            output_schema=schema_registry.get_schema("GetGuideContentResult"),
        ),
        MCPTool(
            function=search_guides,
            description="Search guides using semantic search",
            parameters=JsonSchema(
                type="object",
                properties={
                    "query": JsonSchemaProperty(
                        "string",
                        "The search query",
                        required=True
                    ),
                    "top_k": JsonSchemaProperty(
                        "integer",
                        "Maximum number of results to return",
                        required=False
                    )
                }
            ),
            output_schema=schema_registry.get_schema("SearchGuidesResult"),
        ),
        MCPTool(
            function=rebuild_semantic_index,
            description="Rebuild the semantic search index for guides",
            output_schema=schema_registry.get_schema("RebuildIndexResult"),
        ),
        MCPTool(
            function=get_guide_recommendations,
            description="Get guide recommendations based on topics and filters",
            parameters=JsonSchema(
                type="object",
                properties={
                    "topics": JsonSchemaProperty(
                        "array",
                        "List of topics of interest",
                        items=JsonSchema(type="string"),
                        required=True
                    ),
                    "maturity_level": JsonSchemaProperty(
                        "string",
                        "Filter by maturity level",
                        required=False
                    ),
                    "division": JsonSchemaProperty(
                        "string",
                        "Filter by division",
                        required=False
                    )
                }
            ),
            output_schema=schema_registry.get_schema("SearchGuidesResult"),
        ),
    ]

    # Start MCP server
    server = await setup_mcp_server(
        service_info=SERVICE_INFO,
        tools=tools,
    )
    
    # Print server info
    address = server.sockets[0].getsockname() 
    logger.info(f"Guides MCP Server running at {address[0]}:{address[1]}")
    
    # Keep the server running
    await asyncio.Future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Guides MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", default=8080, type=int, help="Port to bind the server to")
    args = parser.parse_args()
    
    try:
        # Start server with command line arguments
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)