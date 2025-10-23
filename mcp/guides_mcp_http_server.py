#!/usr/bin/env python3
"""
Unified REST API and MCP HTTP Server for Guides

This script creates a Flask application that serves both a REST API and a
Model Context Protocol (MCP) endpoint over HTTP.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

from flask import Flask, jsonify, request, Response, redirect, session, url_for
from mcp.server.fastmcp import FastMCP
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from mcp.model import PublicTool

# --- Configuration ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Google Cloud Project ID
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "requirements-mcp-server")

# --- Flask App Initialization ---

app = Flask(__name__)

# --- Core Logic Functions ---

def get_guides_root() -> Path:
    """Get the guides root directory path."""
    return Path("guides")

def get_search_function():
    """Lazy import for search functionality."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from vector_search import search_guides
    return search_guides

def get_build_index_function():
    """Lazy import for index building functionality."""
    from vector_search import build_index_from_guides
    return build_index_from_guides

def do_list_guide_divisions() -> List[Dict[str, Any]]:
    """Logic for listing all guide divisions."""
    divisions = []
    guides_dir = get_guides_root()
    if not guides_dir.exists():
        return divisions
    
    for division_dir in guides_dir.iterdir():
        if division_dir.is_dir() and division_dir.name not in ("semantic_index", "README.md"):
            guide_count = sum(1 for item in division_dir.iterdir() if item.is_dir())
            divisions.append({"name": division_dir.name, "guide_count": guide_count})
    
    return sorted(divisions, key=lambda x: x["name"])

def do_list_guides_by_division(division: str) -> List[Dict[str, str]]:
    """Logic for listing all guides in a specific division."""
    guides = []
    division_dir = get_guides_root() / division
    
    if not division_dir.exists() or not division_dir.is_dir():
        return guides
    
    for guide_dir in division_dir.iterdir():
        if guide_dir.is_dir() and (index_file := guide_dir / "index.md").exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = "Unknown"
            maturity = "Unknown"
            
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
                "path": str(index_file.relative_to(get_guides_root()))
            })
    
    return sorted(guides, key=lambda x: x["title"])

def do_get_guide_content(guide_path: str) -> Dict[str, Any]:
    """Logic for getting the content of a specific guide."""
    guide_file = get_guides_root() / guide_path
    
    if not guide_file.exists():
        raise FileNotFoundError(f"Guide not found: {guide_path}")
    
    with open(guide_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter = {}
    markdown_content = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_content = parts[1]
            markdown_content = parts[2]
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

def do_search_guides(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Logic for searching guides."""
    search_func = get_search_function()
    results = search_func(query, top_k=top_k)
    return [
        {
            "title": r["title"], "division": r["division"], "file_path": r["file_path"],
            "score": r["score"], "content_preview": r["content_preview"]
        } for r in results
    ]

# --- MCP Server Initialization ---

mcp = FastMCP(
    "Implementation Guides",
    instructions=(
        "Always check implementation guides for software requirements when users ask about building features, implementing modules, or following best practices. "
        "Search guides by topic, get recommendations, or browse by division and maturity level. "
        "Use these tools proactively for any development-related questions."
    )
)

@mcp.tool()
def list_guide_divisions() -> List[Dict[str, Any]]:
    """List all available guide divisions (pm, qa, se, exd)."""
    return do_list_guide_divisions()

@mcp.tool()
def list_guides_by_division(division: str) -> List[Dict[str, str]]:
    """List all guides in a specific division."""
    return do_list_guides_by_division(division)

@mcp.tool()
def get_guide_content(path: str) -> Dict[str, Any]:
    """Get the full content and metadata of a specific guide."""
    try:
        return do_get_guide_content(path)
    except FileNotFoundError as e:
        return {"error": str(e)}

@mcp.tool()
def search_guides(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for guides using semantic search."""
    return do_search_guides(query, top_k)

# --- HTTP Server Endpoints ---

@app.before_request
def check_auth():
    """Check for Google identity token authentication."""
    # Allow health check and index without auth
    if request.path in ["/health", "/"]:
        return None
    
    if request.path == "/mcp":
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header missing or invalid"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Validate the Google identity token
            id_info = id_token.verify_oauth2_token(token, google_requests.Request(), PROJECT_ID)
            # Check if the email domain is allowed (you-source.com)
            email = id_info.get('email', '')
            if not email.endswith('@you-source.com'):
                return jsonify({"error": "Access denied: Invalid domain"}), 403
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return jsonify({"error": "Invalid authentication token"}), 403

@app.route("/mcp", methods=["POST"])
async def mcp_endpoint():
    """MCP endpoint to handle JSON-RPC requests."""
    request_json = request.get_json()
    response_json = await mcp.handle(request_json)
    if response_json:
        return jsonify(response_json)
    return Response(status=204)

@app.route("/", methods=["GET"])
def index():
    """Service information endpoint."""
    return jsonify({
        "service": "Implementation Guides MCP Server",
        "version": "0.2.0",
        "mcp_endpoint": "/mcp"
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
