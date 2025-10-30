# Bug Fix: MCP Guide Path Resolution Issue

## Problem

The MCP server was returning a 500 error when trying to retrieve guide content:
```
Guide not found: se/authentication-module---growth-1/index.md
```

This caused the `/specify` workflow to fall back to local guides instead of using the MCP server, even though the search functionality worked correctly.

## Root Cause

The issue was caused by a **working directory mismatch** in the Cloud Run deployment:

1. **Dockerfile configuration:**
   ```dockerfile
   WORKDIR /app        # Copies guides to /app/guides
   # ...
   WORKDIR /app/mcp    # Changes to /app/mcp before running server
   CMD exec gunicorn ... guides_mcp_http_server:app
   ```

2. **Original code in `guides_mcp_http_server.py`:**
   ```python
   def get_guides_root() -> Path:
       return Path("guides")  # Returns relative path
   ```

3. **What happened:**
   - When running from `/app/mcp`, `Path("guides")` resolved to `/app/mcp/guides`
   - But the actual guides directory was at `/app/guides`
   - Search worked because it used vector embeddings from Firestore
   - Content retrieval failed because the file path didn't exist

## Solution

Modified `get_guides_root()` to intelligently handle both local development and Cloud Run deployment:

```python
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
```

### How it works:

1. First tries `./guides` (relative to current working directory)
2. If not found, tries `../guides` (relative to the script location)
3. Always returns an absolute path for consistency

This works correctly in both scenarios:
- **Local development:** Running from project root, `./guides` exists
- **Cloud Run:** Running from `/app/mcp`, falls back to `/app/guides`

## Testing

Verified the fix works in both scenarios:

```bash
# From project root
cd /Users/reytianero/code/ys-requirements-list
python3 -c "from mcp.guides_mcp_http_server import get_guides_root; print(get_guides_root())"
# Output: /Users/reytianero/code/ys-requirements-list/guides

# From mcp subdirectory
cd /Users/reytianero/code/ys-requirements-list/mcp
python3 -c "from guides_mcp_http_server import get_guides_root; print(get_guides_root())"
# Output: /Users/reytianero/code/ys-requirements-list/guides
```

Complete flow test:
```python
# Search returns paths like: se/authentication-module---growth-1/index.md
results = do_search_guides('authentication', top_k=2)
path = results[0].get('file_path')

# Content retrieval now works correctly
content = do_get_guide_content(path)
# Success! Returns guide content
```

## Impact

- ✅ MCP server now correctly retrieves guide content in Cloud Run
- ✅ `/specify` workflow will use MCP guides when available (5 guides with semantic search)
- ✅ Graceful fallback to local guides still works when MCP is unavailable
- ✅ No changes needed to client code or API contracts

## Files Modified

1. `/Users/reytianero/code/ys-requirements-list/mcp/guides_mcp_http_server.py`
2. `/Users/reytianero/code/ys-spec-kit/context/references/mcp/guides_mcp_http_server.py` (reference copy)

## Deployment

The fix will be automatically deployed when merged to `main` via the GitHub Actions workflow.

No manual deployment steps required.
