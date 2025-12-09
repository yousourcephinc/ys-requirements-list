#!/usr/bin/env python3
"""
Unified REST API and MCP HTTP Server for Guides

This script creates a Flask application that serves both a REST API and a
Model Context Protocol (MCP) endpoint over HTTP.
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests

from flask import Flask, jsonify, request, Response, redirect, session, url_for
# from mcp.server.fastmcp import FastMCP  # Commented out for HTTP-only server
# from google.oauth2 import id_token  # Commented out - auth disabled
# from google.auth.transport import requests as google_requests  # Commented out - auth disabled

# --- Configuration ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Google Cloud Project ID
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "requirements-mcp-server")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")

# --- Query Expansion Cache ---
# Simple in-memory cache for expanded queries (TTL: 1 hour)
_expansion_cache: Dict[str, tuple] = {}  # {query: (expanded_terms, timestamp)}
CACHE_TTL_SECONDS = 3600  # 1 hour

# --- Flask App Initialization ---

app = Flask(__name__)

# --- Core Logic Functions ---

def get_guides_root() -> Path:
    """Get the guides root directory path."""
    # If running from /app/mcp (Cloud Run), guides are at /app/guides
    # If running from project root locally, guides are at ./guides
    guides_path = Path("guides")
    if not guides_path.exists():
        # Try parent directory (for when running from mcp/ subdirectory)
        parent_guides = Path(__file__).parent.parent / "guides"
        if parent_guides.exists():
            return parent_guides
    return guides_path.absolute()

def get_search_function():
    """Lazy import for search functionality with fallback."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    try:
        from vector_search import search_guides
        return search_guides
    except ImportError as e:
        logger.warning(f"Could not import vector_search: {e}. Using simple text search.")
        # Fallback to simple text search
        def simple_search_guides(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
            """Simple text-based search through guide content."""
            results = []
            guides_dir = get_guides_root()
            
            # Search through all guide files
            for guide_file in guides_dir.rglob("*.md"):
                try:
                    with open(guide_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple text matching
                    if query.lower() in content.lower():
                        # Extract basic info
                        title = guide_file.stem.replace('-', ' ').title()
                        division = guide_file.parent.parent.name if guide_file.parent.parent != guides_dir else 'unknown'
                        
                        # Get preview
                        lines = content.split('\n')
                        preview = ' '.join(lines[:3])[:200] + '...'
                        
                        results.append({
                            "title": title,
                            "division": division,
                            "file_path": str(guide_file.relative_to(guides_dir)),
                            "score": 0.5,  # Placeholder score
                            "content_preview": preview
                        })
                        
                        if len(results) >= top_k:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error reading {guide_file}: {e}")
                    continue
                    
            return results
        
        return simple_search_guides

def get_build_index_function():
    """Lazy import for index building functionality with fallback."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    try:
        from vector_search import build_index_from_guides
        return build_index_from_guides
    except ImportError as e:
        logger.warning(f"Could not import vector_search: {e}. Index building not available.")
        def placeholder_build_index():
            return {"status": "not implemented", "error": str(e)}
        return placeholder_build_index

def do_list_guide_divisions() -> List[Dict[str, Any]]:
    """List only the 'se' guide division with its guide count."""
    divisions = []
    guides_dir = get_guides_root()
    if guides_dir.exists() and guides_dir.is_dir():
        se_dir = guides_dir / 'se'
        if se_dir.is_dir():
            guide_count = len(list(se_dir.glob('**/*')))
            divisions.append({"name": "se", "guide_count": guide_count})
    return divisions

def do_list_guides_by_division(division: str) -> List[Dict[str, str]]:
    """Logic for listing all guides in a specific division."""
    guides = []
    
    # If a division is specified, and it's not 'se', return empty list
    if division and division.lower() != 'se':
        return []

    # Default to 'se' if no division is specified or if it is 'se'
    division_to_scan = 'se'
    division_dir = get_guides_root() / division_to_scan
    
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


def _get_cached_expansion(query: str) -> Optional[List[str]]:
    """Get cached expansion if still valid."""
    if query in _expansion_cache:
        terms, timestamp = _expansion_cache[query]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            logger.info(f"Cache hit for query: {query[:50]}...")
            return terms
        else:
            del _expansion_cache[query]
    return None


def _cache_expansion(query: str, terms: List[str]) -> None:
    """Cache expanded terms with timestamp."""
    _expansion_cache[query] = (terms, time.time())
    # Limit cache size to 1000 entries
    if len(_expansion_cache) > 1000:
        oldest = min(_expansion_cache.items(), key=lambda x: x[1][1])
        del _expansion_cache[oldest[0]]


def _expand_query_with_vertex(query: str, max_terms: int = 4) -> List[str]:
    """
    Use Vertex AI to expand a query into related technical search terms.
    
    Args:
        query: User's input (feature, task, question, etc.)
        max_terms: Maximum number of additional terms to generate
        
    Returns:
        List of search terms including the original query
    """
    # Check cache first
    cached = _get_cached_expansion(query)
    if cached:
        return cached
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=GCP_LOCATION)
        
        model = GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""Given this software development query, generate {max_terms} related technical search terms for finding implementation guides.

Query: "{query}"

Return ONLY a comma-separated list of short technical terms (2-4 words each). No explanations, no numbering.
Focus on: module names, design patterns, security concerns, integration points.

Example input: "user wants to upload avatar"
Example output: file upload, image processing, profile management, media storage"""

        response = model.generate_content(prompt)
        
        # Parse response into list
        terms = [t.strip() for t in response.text.split(',') if t.strip()]
        terms = [t for t in terms if len(t) < 50]  # Filter out long responses
        
        # Always include original query first
        result = [query] + terms[:max_terms]
        
        # Cache the result
        _cache_expansion(query, result)
        
        logger.info(f"Expanded '{query[:30]}...' to {len(result)} terms")
        return result
        
    except Exception as e:
        logger.warning(f"Vertex expansion failed: {e}. Using original query only.")
        return [query]


def do_search_guides(query: str, top_k: int = 5, expand: bool = True) -> List[Dict[str, Any]]:
    """
    Search guides with automatic query expansion via Vertex AI.
    
    Args:
        query: Search query (any format: user story, feature, question, etc.)
        top_k: Maximum results to return
        expand: Whether to expand query with Vertex AI (default: True)
    
    Returns:
        List of matching guides with scores
    """
    search_func = get_search_function()
    
    # Expand query into multiple search terms
    search_terms = _expand_query_with_vertex(query) if expand else [query]
    
    all_results = []
    seen_paths = set()
    
    for term in search_terms:
        try:
            results = search_func(term, top_k=top_k)
            for r in results:
                path = r.get('file_path', '')
                if path and path not in seen_paths:
                    seen_paths.add(path)
                    # Boost score for original query matches
                    if term == query:
                        r['score'] = r.get('score', 0) * 1.1
                    all_results.append(r)
        except Exception as e:
            logger.warning(f"Search failed for '{term}': {e}")
            # Fallback to simple text search for this term
            _fallback_text_search(term, top_k, all_results, seen_paths)
    
    # Sort by score and return top_k
    all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    return all_results[:top_k]


def _fallback_text_search(
    query: str, 
    top_k: int, 
    results: List[Dict], 
    seen_paths: set
) -> None:
    """Simple text search fallback when vector search fails."""
    guides_dir = get_guides_root()
    
    for guide_file in guides_dir.rglob("*.md"):
        if len(results) >= top_k:
            break
        try:
            with open(guide_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if query.lower() in content.lower():
                path = str(guide_file.relative_to(guides_dir))
                if path in seen_paths:
                    continue
                seen_paths.add(path)
                
                title = guide_file.stem.replace('-', ' ').title()
                division = guide_file.parent.parent.name if guide_file.parent.parent != guides_dir else 'unknown'
                lines = content.split('\n')
                preview = ' '.join(lines[:3])[:200] + '...'
                
                results.append({
                    "title": title,
                    "division": division,
                    "file_path": path,
                    "score": 0.5,
                    "content_preview": preview
                })
        except Exception as e:
            logger.warning(f"Error reading {guide_file}: {e}")


# --- MCP Server Initialization ---
# FastMCP disabled for HTTP-only server - using direct function calls instead

# mcp = FastMCP(
#     "Implementation Guides",
#     instructions=(
#         "Always check implementation guides for software requirements when users ask about building features, implementing modules, or following best practices. "
#         "Search guides by topic, get recommendations, or browse by division and maturity level. "
#         "Use these tools proactively for any development-related questions."
#     )
# )

# @mcp.tool()
# def list_guide_divisions() -> List[Dict[str, Any]]:
#     """List all available guide divisions (pm, qa, se, exd)."""
#     return do_list_guide_divisions()

# @mcp.tool()
# def list_guides_by_division(division: str) -> List[Dict[str, str]]:
#     """List all guides in a specific division."""
#     return do_list_guides_by_division(division)

# @mcp.tool()
# def get_guide_content(path: str) -> Dict[str, Any]]:
#     """Get the full content and metadata of a specific guide."""
#     try:
#         return do_get_guide_content(path)
#     except FileNotFoundError as e:
#         return {"error": str(e)}

# @mcp.tool()
# def search_guides(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
#     """Search for guides using semantic search (Vertex AI) when available, otherwise text search."""
#     return do_search_guides(query, top_k)

# --- HTTP Server Endpoints ---

# API Key for authentication (set via environment variable or use default)
API_KEY = os.environ.get("MCP_API_KEY", "test-key")

@app.before_request
def check_auth():
    """Authentication is disabled for all endpoints."""
    logger.info(f"Request to {request.path} - Authentication disabled.")
    return None

# --- REST API Endpoints ---
# These provide direct REST access to guide functionality without MCP protocol

@app.route("/divisions", methods=["GET"])
def api_list_divisions():
    """REST API: List all guide divisions with counts."""
    try:
        divisions = do_list_guide_divisions()
        return jsonify(divisions)
    except Exception as e:
        logger.error(f"Error listing divisions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/divisions/<division>/guides", methods=["GET"])
def api_list_guides(division: str):
    """REST API: List all guides in a specific division."""
    try:
        guides = do_list_guides_by_division(division)
        return jsonify(guides)
    except Exception as e:
        logger.error(f"Error listing guides for {division}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/guides/<path:guide_path>", methods=["GET"])
def api_get_guide(guide_path: str):
    """REST API: Get full content of a specific guide."""
    try:
        content = do_get_guide_content(guide_path)
        return jsonify(content)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting guide {guide_path}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["POST"])
def api_search_guides():
    """REST API: Search guides using semantic search."""
    try:
        data = request.get_json() or {}
        query = data.get("query", "")
        top_k = data.get("top_k", 5)
        
        if not query:
            return jsonify({"error": "query parameter is required"}), 400
        
        results = do_search_guides(query, top_k=top_k)
        return jsonify({"results": results, "query": query, "count": len(results)})
    except Exception as e:
        logger.error(f"Error searching guides: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/recommendations", methods=["POST"])
def api_get_recommendations():
    """REST API: Get guide recommendations based on topics."""
    try:
        data = request.get_json() or {}
        topics = data.get("topics", [])
        division = data.get("division", "se")
        top_k = data.get("top_k", 5)
        
        if not topics:
            return jsonify({"error": "topics parameter is required"}), 400
        
        # Combine topics into search query
        query = " ".join(topics)
        results = do_search_guides(query, top_k=top_k)
        
        # Filter by division if specified
        if division:
            results = [r for r in results if r.get("division", "").lower() == division.lower()]
        
        return jsonify({"recommendations": results[:top_k], "topics": topics})
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    """MCP endpoint to handle JSON-RPC requests (POST) and SSE connections (GET)."""
    
    # Handle GET request for SSE/streaming (VS Code MCP client uses this)
    if request.method == "GET":
        logger.info("GET request to /mcp - starting SSE stream")
        
        def stream():
            # Send the endpoint event pointing to the same URL for POST requests
            # The client will send JSON-RPC requests to this endpoint
            yield "event: endpoint\ndata: /mcp\n\n"
            
            # Keep the connection open with keepalive comments
            import time
            while True:
                time.sleep(10)
                yield ": keepalive\n\n"
                
        return Response(stream(), mimetype='text/event-stream')
    
    # Handle POST request for JSON-RPC
    request_json = request.get_json()
    
    # Handle MCP JSON-RPC requests manually
    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")
    
    try:
        if method == "initialize":
            # MCP protocol initialization handshake
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "Implementation Guides MCP Server",
                    "version": "0.2.0"
                }
            }
        elif method == "notifications/initialized":
            # Handle initialized notification (no response needed for notifications)
            logger.info("Received notifications/initialized")
            return jsonify({"jsonrpc": "2.0", "result": None}), 200
        elif method == "tools/list":
            # Return the list of available tools
            tools_data = [
                {
                    "name": "list_guide_divisions",
                    "description": "List all available guide divisions (pm, qa, se, exd).",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "list_guides_by_division", 
                    "description": "List all guides in a specific division.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "division": {"type": "string", "description": "Division name (pm, qa, se, exd)"}
                        },
                        "required": ["division"]
                    }
                },
                {
                    "name": "get_guide_content",
                    "description": "Get the full content and metadata of a specific guide.",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "path": {"type": "string", "description": "Path to the guide"}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "search_guides",
                    "description": "Search for guides using semantic search when available, otherwise text search.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "top_k": {"type": "integer", "description": "Number of results", "default": 3}
                        },
                        "required": ["query"]
                    }
                }
            ]
            result = {"tools": tools_data}
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Call the appropriate tool function directly
            if tool_name == "list_guide_divisions":
                result = {"content": [{"type": "text", "text": str(do_list_guide_divisions())}]}
            elif tool_name == "list_guides_by_division":
                division = arguments.get("division")
                result = {"content": [{"type": "text", "text": str(do_list_guides_by_division(division))}]}
            elif tool_name == "get_guide_content":
                path = arguments.get("path")
                result = {"content": [{"type": "text", "text": str(do_get_guide_content(path))}]}
            elif tool_name == "search_guides":
                query = arguments.get("query")
                top_k = arguments.get("top_k", 3)
                result = {"content": [{"type": "text", "text": str(do_search_guides(query, top_k))}]}
            else:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }), 404
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }), 404
        
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        })
    except Exception as e:
        logger.error(f"MCP endpoint error: {e}")
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(e)}
        }), 500

@app.route("/", methods=["GET"])
def index():
    """Service information endpoint."""
    return jsonify({
        "service": "Implementation Guides MCP Server",
        "version": "0.3.0",
        "mcp_endpoint": "/mcp",
        "rest_endpoints": {
            "GET /divisions": "List all guide divisions",
            "GET /divisions/<division>/guides": "List guides in a division",
            "GET /guides/<path>": "Get guide content",
            "POST /search": "Search guides (body: {query, top_k})",
            "POST /recommendations": "Get recommendations (body: {topics, division, top_k})"
        }
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
