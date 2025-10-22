#!/usr/bin/env python3
# /// script
# dependencies = [
#   "mcp>=1.2.0",
#   "httpx>=0.27.0",
# ]
# ///
"""Implementation Guides MCP Server

Provides access to implementation guides via Model Context Protocol.
"""

import subprocess
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with instructions
mcp = FastMCP(
    "Implementation Guides",
    instructions=(
        "Access implementation guides for software modules across PM, QA, SE, and Experience Design. "
        "Search guides by topic, get recommendations, or browse by division and maturity level. "
        "All operations require Google Cloud authentication via gcloud CLI."
    )
)

# Constants
BASE_URL = "https://mcp-server-375955300575.us-central1.run.app"


def get_auth_token() -> str:
    """Get Google Cloud authentication token using gcloud CLI"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-identity-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get auth token. Make sure you're authenticated with 'gcloud auth login': {e}")


async def api_request(method: str, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make authenticated request to the Guides API"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{path}", headers=headers)
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{path}", headers=headers, json=json_data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_guide_divisions() -> list[dict[str, Any]]:
    """List all available guide divisions.
    
    Returns information about each division including:
    - name: Division identifier (pm, qa, se, exd)
    - guide_count: Number of guides in the division
    """
    return await api_request("GET", "/divisions")


@mcp.tool()
async def list_guides_by_division(division: str) -> list[dict[str, str]]:
    """List all guides in a specific division.
    
    Args:
        division: Division name (pm, qa, se, or exd)
    
    Returns:
        List of guides with title, maturity level, and path
    """
    return await api_request("GET", f"/divisions/{division}/guides")


@mcp.tool()
async def get_guide_content(path: str) -> dict[str, Any]:
    """Get the full content and metadata of a specific guide.
    
    Args:
        path: Full path to the guide (e.g., 'se/authentication-module---introduction-1/index.md')
    
    Returns:
        Guide content including markdown text, metadata, and requirements
    """
    return await api_request("GET", f"/guides/{path}")


@mcp.tool()
async def search_guides(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Search for guides using semantic search.
    
    Args:
        query: Search query describing what you're looking for
        top_k: Number of results to return (default: 3, max: 10)
    
    Returns:
        List of relevant guides with similarity scores
    """
    return await api_request("POST", "/search", {"query": query, "top_k": top_k})


@mcp.tool()
async def get_guide_recommendations(
    topics: list[str],
    maturity_level: str | None = None,
    division: str | None = None
) -> list[dict[str, Any]]:
    """Get personalized guide recommendations based on topics and filters.
    
    Args:
        topics: List of topics you're interested in (e.g., ["authentication", "security"])
        maturity_level: Filter by maturity level (e.g., "Introduction 1", "Growth 1")
        division: Filter by division (pm, qa, se, or exd)
    
    Returns:
        Top 5 recommended guides matching your criteria
    """
    data = {"topics": topics}
    if maturity_level:
        data["maturity_level"] = maturity_level
    if division:
        data["division"] = division
    
    return await api_request("POST", "/recommendations", data)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
