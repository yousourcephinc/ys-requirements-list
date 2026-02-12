# ys-guides

Claude Code plugin that connects to the YS Implementation Guides MCP server, providing semantic search across SE, PM, QA, and EXD implementation guides.

## Tools

Once enabled, Claude Code gains access to these tools:

| Tool | Description |
|------|-------------|
| `list_guide_divisions` | List all guide divisions with counts |
| `list_guides_by_division` | List guides in a specific division |
| `get_guide_content` | Get full guide content and metadata |
| `search_guides` | Semantic search across all guides |

## Prerequisites

- Python 3.10+
- Google Cloud SDK authenticated (`gcloud auth application-default login`)
- `httpx` and `google-auth` Python packages

Install dependencies:

```bash
pip install httpx google-auth google-auth-httplib2
```

## Setup

1. Authenticate with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

2. Enable the plugin in Claude Code:
   ```bash
   claude --plugin-dir ./ys-guides
   ```

3. Verify the MCP server connects:
   ```
   /mcp
   ```

## Configuration

The MCP server URL defaults to the Cloud Run deployment. Override with the `MCP_SERVER_URL` environment variable if needed.
