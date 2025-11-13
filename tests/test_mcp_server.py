#!/usr/bin/env python3
"""
Simplified MCP HTTP Server for testing (without FastMCP dependency).
"""

import os
import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, jsonify, request

# Add the parent directory to Python path to import from mcp folder
sys.path.append(str(Path(__file__).parent / "mcp"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Import the core functions
from guides_mcp_http_server import (
    do_list_guide_divisions,
    do_list_guides_by_division, 
    do_get_guide_content,
    do_search_guides
)

@app.route("/", methods=["GET"])
def index():
    """Service information endpoint."""
    return jsonify({
        "service": "Implementation Guides MCP Server (Test)",
        "version": "0.3.0",
        "mcp_endpoint": "/mcp",
        "available_tools": [
            "list_guide_divisions",
            "list_guides_by_division", 
            "get_guide_content",
            "search_guides"
        ]
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route("/test/divisions", methods=["GET"])
def test_divisions():
    """Test endpoint for divisions."""
    try:
        divisions = do_list_guide_divisions()
        return jsonify({"divisions": divisions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test/guides/<division>", methods=["GET"])
def test_guides(division):
    """Test endpoint for guides by division."""
    try:
        guides = do_list_guides_by_division(division)
        return jsonify({"guides": guides})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test/search", methods=["POST"])
def test_search():
    """Test endpoint for search."""
    try:
        data = request.get_json()
        query = data.get("query", "")
        top_k = data.get("top_k", 3)
        results = do_search_guides(query, top_k)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """Simplified MCP endpoint."""
    try:
        request_json = request.get_json()
        method = request_json.get("method")
        params = request_json.get("params", {})
        request_id = request_json.get("id")
        
        if method == "tools/list":
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
                    "name": "search_guides",
                    "description": "Search for guides using text search.",
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
            
            if tool_name == "list_guide_divisions":
                divisions = do_list_guide_divisions()
                result = {"content": [{"type": "text", "text": json.dumps(divisions, indent=2)}]}
            elif tool_name == "search_guides":
                query = arguments.get("query")
                top_k = arguments.get("top_k", 3)
                search_results = do_search_guides(query, top_k)
                result = {"content": [{"type": "text", "text": json.dumps(search_results, indent=2)}]}
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    print(f"Starting simplified MCP server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)