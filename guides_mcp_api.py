#!/usr/bin/env python3
"""
REST API Server for Guides

This script creates a Flask REST API that exposes tools to interact with the guides.

Usage:
  python guides_mcp_api.py
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, jsonify, request

# Import guide-related functions from sync_notion
from sync_notion import (
    search_semantic_index,
    GUIDES_ROOT_DIR,
    build_semantic_index,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- API Endpoints ---

@app.route("/", methods=["GET"])
def index():
    """API information endpoint."""
    return jsonify({
        "service": "Guides API",
        "version": "0.1.0",
        "description": "REST API providing tools to interact with implementation guides",
        "endpoints": {
            "/divisions": "List all divisions (categories) of guides",
            "/divisions/<division>/guides": "List all guides in a specific division",
            "/guides/<path:guide_path>": "Get the content of a specific guide",
            "/search": "Search guides using semantic search (POST with 'query' and optional 'top_k')",
            "/rebuild-index": "Rebuild the semantic search index (POST)",
            "/recommendations": "Get guide recommendations (POST with 'topics', optional 'maturity_level', 'division')"
        }
    })


@app.route("/divisions", methods=["GET"])
def list_guide_divisions():
    """
    List all divisions (categories) of guides in the repository.
    
    Returns:
        JSON array of divisions with their name and guide count.
    """
    divisions = []
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    if not guides_dir.exists():
        return jsonify(divisions)
    
    for division_dir in guides_dir.iterdir():
        if division_dir.is_dir() and division_dir.name not in ("semantic_index", "README.md"):
            guide_count = 0
            for item in division_dir.iterdir():
                if item.is_dir():
                    guide_count += 1
                    
            divisions.append({
                "name": division_dir.name,
                "guide_count": guide_count
            })
    
    return jsonify(sorted(divisions, key=lambda x: x["name"]))


@app.route("/divisions/<division>/guides", methods=["GET"])
def list_guides_by_division(division: str):
    """
    List all guides in a specific division.
    
    Args:
        division: The division (category) name to list guides from
        
    Returns:
        JSON array of guides in the specified division.
    """
    guides = []
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    division_dir = guides_dir / division
    
    if not division_dir.exists() or not division_dir.is_dir():
        return jsonify(guides)
    
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
    
    return jsonify(sorted(guides, key=lambda x: x["title"]))


@app.route("/guides/<path:guide_path>", methods=["GET"])
def get_guide_content(guide_path: str):
    """
    Get the content of a specific guide.
    
    Args:
        guide_path: Relative path to the guide index file (e.g., "pm/user-management/index.md")
        
    Returns:
        JSON object with guide content and metadata
    """
    guides_dir = Path(GUIDES_ROOT_DIR)
    guide_file = guides_dir / guide_path
    
    if not guide_file.exists():
        return jsonify({
            "error": "Guide not found",
            "guide_path": guide_path
        }), 404
    
    try:
        with open(guide_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse frontmatter and content
        frontmatter = {}
        markdown_content = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_content = parts[1]
                markdown_content = parts[2]
                
                # Parse frontmatter
                for line in frontmatter_content.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"')
        
        return jsonify({
            "title": frontmatter.get("title", "Untitled"),
            "division": frontmatter.get("division", "Unknown"),
            "maturity": frontmatter.get("maturity", "Unknown"),
            "source_url": frontmatter.get("source_url", ""),
            "content": markdown_content.strip(),
            "path": guide_path
        })
    except Exception as e:
        logger.error(f"Error reading guide: {str(e)}")
        return jsonify({
            "error": f"Error reading guide: {str(e)}",
            "guide_path": guide_path
        }), 500


@app.route("/search", methods=["POST"])
def search_guides():
    """
    Search guides using semantic search.
    
    Request JSON:
        query: The search query
        top_k: Maximum number of results to return (default: 5)
        
    Returns:
        JSON array of matching guide results
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    query = data['query']
    top_k = data.get('top_k', 5)
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    
    # Check if index exists, if not build it
    index_dir = guides_dir / "semantic_index"
    if not (index_dir / "guides.index").exists():
        logger.info("Semantic index not found, building it first...")
        try:
            build_semantic_index(guides_dir)
        except Exception as e:
            logger.error(f"Error building semantic index: {str(e)}")
            return jsonify({"error": f"Failed to build semantic index: {str(e)}"}), 500
    
    try:
        results = search_semantic_index(query, guides_dir, top_k=top_k)
        
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
        
        return jsonify(formatted_results)
    except Exception as e:
        logger.error(f"Error searching guides: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


@app.route("/rebuild-index", methods=["POST"])
def rebuild_semantic_index():
    """
    Rebuild the semantic search index for guides.
    
    Returns:
        JSON object with status of the indexing operation
    """
    guides_dir = Path(GUIDES_ROOT_DIR)
    
    try:
        logger.info("Rebuilding semantic search index...")
        build_semantic_index(guides_dir)
        return jsonify({
            "success": True,
            "message": "Semantic index rebuilt successfully"
        })
    except Exception as e:
        logger.error(f"Error rebuilding semantic index: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error rebuilding semantic index: {str(e)}"
        }), 500


@app.route("/recommendations", methods=["POST"])
def get_guide_recommendations():
    """
    Get guide recommendations based on topics and filters.
    
    Request JSON:
        topics: List of topics of interest
        maturity_level: Filter by maturity level (optional)
        division: Filter by division (optional)
        
    Returns:
        JSON array of recommended guides
    """
    data = request.get_json()
    if not data or 'topics' not in data:
        return jsonify({"error": "Missing 'topics' parameter"}), 400
    
    topics = data['topics']
    maturity_level = data.get('maturity_level')
    division = data.get('division')
    
    if not isinstance(topics, list):
        return jsonify({"error": "'topics' must be an array"}), 400
    
    guides_dir = Path(GUIDES_ROOT_DIR)
    
    # Build combined query from topics
    query = " ".join(topics)
    
    try:
        # Get initial results from semantic search
        results = search_semantic_index(query, guides_dir, top_k=10)
        
        # Filter results if needed
        filtered_results = []
        for result in results:
            include = True
            
            if maturity_level and "maturity" in result:
                # Check if maturity level matches (case-insensitive)
                if result.get("maturity", "").lower() != maturity_level.lower():
                    include = False
                    
            if division and result["division"].lower() != division.lower():
                include = False
                
            if include:
                filtered_results.append({
                    "title": result["title"],
                    "division": result["division"],
                    "file_path": result["file_path"],
                    "score": result["score"],
                    "content_preview": result["content_preview"]
                })
        
        # Return top 5 after filtering
        return jsonify(filtered_results[:5])
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({"error": f"Failed to get recommendations: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
