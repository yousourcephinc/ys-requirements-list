# Implementation Guides MCP Server

Access implementation guides from AI assistants using the Model Context Protocol (MCP).

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open standard that lets AI assistants like Claude connect to external data sources and tools. This MCP server provides access to our implementation guides library through a standardized interface.

## Quick Start

```bash
# 1. Authenticate with Google Cloud
gcloud auth login

# 2. Install to Claude Desktop
```bash
cd /path/to/ys-requirements-list
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"
```

# 3. Restart Claude Desktop
```

**Zero Installation Required:** The script uses PEP 723 inline dependencies - `uv` automatically installs `mcp` and `httpx` on first run. No manual dependency management needed!

## Architecture

```
┌─────────────────┐
│  Claude Desktop │  ← MCP Client
│   (or others)   │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ▼
┌─────────────────┐
│   Local MCP     │  ← This Repository
│     Server      │     (guides_mcp_wrapper.py)
│   (FastMCP)     │
└────────┬────────┘
         │ HTTPS + OAuth
         ▼
┌─────────────────┐
│   Cloud Run     │  ← Backend Service
│   REST API      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vertex AI +    │  ← AI/Storage
│   Firestore     │
└─────────────────┘
```

## Available Tools

Once installed, AI assistants have access to **5 tools**:

### 1. `list_guide_divisions`
Lists all divisions (pm, qa, se, exd) with guide counts.

**Returns:** Array of division objects with name and guide_count

### 2. `list_guides_by_division` 
Lists all guides in a specific division.

**Parameters:**
- `division` (string): pm, qa, se, or exd

**Returns:** Array of guides with title, maturity level, and path

### 3. `get_guide_content`
Retrieves the full content and metadata of a specific guide.

**Parameters:**
- `path` (string): Full path like 'se/authentication-module---introduction-1/index.md'

**Returns:** Guide content including markdown text, metadata, and requirements

### 4. `search_guides`
Semantic search across all guides using AI embeddings.

**Parameters:**
- `query` (string): Natural language search query
- `top_k` (integer, optional): Number of results (default: 3, max: 10)

**Returns:** List of relevant guides with similarity scores

### 5. `get_guide_recommendations`
Get personalized recommendations based on topics and filters.

**Parameters:**
- `topics` (list[string]): Topics like ["authentication", "security"]
- `maturity_level` (string, optional): Filter by level like "Introduction 1"
- `division` (string, optional): Filter by division (pm, qa, se, or exd)

**Returns:** Top 5 recommended guides matching criteria

## Usage Examples

In Claude Desktop, you can now ask:

- **"What implementation guides are available for software engineers?"**
  → Uses `list_guides_by_division` with division="se"

- **"Search for authentication guides"**
  → Uses `search_guides` with semantic search

- **"Show me Introduction 1 guides about payments"**
  → Uses `get_guide_recommendations` with filters

- **"Get the user management guide content"**
  → Uses `get_guide_content` to retrieve full markdown

Claude automatically selects the right tools and presents results in natural language.

## Development

### Testing with MCP Inspector

The MCP SDK includes an interactive inspector (dependencies auto-installed):

```bash
uv run mcp dev mcp/guides_mcp_server.py
```

This opens a UI where you can test each tool interactively.

### Direct Execution

Run the server directly (dependencies auto-installed):

```bash
uv run mcp/guides_mcp_server.py
```

The server communicates via stdin/stdout using the MCP protocol.

**Note:** Always use `uv run` - it automatically installs dependencies on first run.

## Implementation Details

- **Framework**: [FastMCP](https://modelcontextprotocol.github.io/python-sdk/) from the official MCP Python SDK
- **Python Version**: 3.10 or higher required
- **Dependencies**: `mcp>=1.2.0`, `httpx>=0.27.0` (auto-installed via PEP 723)
- **Authentication**: Google Cloud Identity via `gcloud auth print-identity-token`
- **Transport**: stdio-based JSON-RPC (standard MCP protocol)
- **Server Instructions**: Built-in guidance for AI assistants on capabilities

## File Structure

- `guides_mcp_server.py` - FastMCP server implementation
- `pyproject.toml` - Python project configuration
- `MCP_SETUP.md` - Detailed installation guide
- `.github/copilot-instructions.md` - GitHub Copilot integration

## Security

- No credentials stored in configuration files
- Uses your personal gcloud authentication
- API calls authenticated via Google Workspace domain
- Server runs locally on your machine

## Troubleshooting

### "Import mcp.server.fastmcp could not be resolved"

This shouldn't happen with `uv run` - dependencies are auto-installed. If you see this:

1. Make sure you're using `uv run` (not direct `python`)
2. Check that the script has inline dependencies declared
3. Try: `uv run --refresh guides_mcp_server.py`

### "Failed to get auth token"

Authenticate with gcloud:
```bash
gcloud auth login
```

### Tools not showing in Claude Desktop

1. Check config file: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Verify the path to the repository is absolute
3. Restart Claude Desktop completely
4. Check logs: `~/Library/Logs/Claude/mcp*.log`

## Links

- [MCP Documentation](https://modelcontextprotocol.io)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Guide](https://modelcontextprotocol.github.io/python-sdk/)
- [Cloud Run API](https://mcp-server-375955300575.us-central1.run.app)

## License

Internal use only - You Source Philippines Inc.
