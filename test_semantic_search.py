#!/usr/bin/env python3
"""Test script for semantic search functionality.

Usage:
  python test_semantic_search.py "your search query"
"""

import sys
import os
from pathlib import Path

# Add current directory to path so we can import sync_notion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_notion import search_semantic_index

def test_semantic_search():
    """Test semantic search functionality."""
    if len(sys.argv) < 2:
        print("Usage: python test_semantic_search.py \"your search query\"")
        print("\nExample queries:")
        print("  python test_semantic_search.py \"authentication setup\"")
        print("  python test_semantic_search.py \"database design patterns\"")
        print("  python test_semantic_search.py \"API security\"")
        return

    query = sys.argv[1]
    guides_dir = Path("guides")

    if not guides_dir.exists():
        print("❌ Guides directory not found. Run sync_notion.py first.")
        return

    print(f"🔍 Searching for: \"{query}\"")
    print("=" * 50)

    results = search_semantic_index(query, guides_dir, top_k=5)

    if not results:
        print("❌ No results found. Make sure semantic index exists.")
        return

    for i, result in enumerate(results, 1):
        print(f"\n{i}. **{result['title']}** ({result['division']})")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Path: guides/{result['file_path']}")
        print(f"   Preview: {result['content_preview']}")
        print("-" * 50)

if __name__ == "__main__":
    test_semantic_search()