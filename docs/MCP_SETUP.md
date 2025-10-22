# Implementation Guides MCP Server Setup

Connect to implementation guides from MCP clients like Claude Desktop using the standard MCP installation process.

## Prerequisites

- **Python 3.10 or higher** installed on your system
- **[uv](https://docs.astral.sh/uv/) package manager** - Install with:
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Windows
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Google Cloud SDK** (`gcloud` CLI) - [Install guide](https://cloud.google.com/sdk/docs/install)
- **Authenticated Google Workspace account:**
  ```bash
  gcloud auth login
  ```

## Installation

### Option 1: Quick Install (Recommended)

Single command installation:

```bash
cd /path/to/ys-requirements-list
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"
```

This command:
- ✅ Automatically installs dependencies (`mcp`, `httpx`) via inline script metadata
- ✅ Adds server configuration to Claude Desktop
- ✅ Sets up authentication to use your gcloud credentials

### Option 2: Manual Configuration

If you prefer manual setup or uv is not available:

1. **Locate Config File:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add Server Configuration:**
   ```json
   {
     "mcpServers": {
       "implementation-guides": {
          "command": "uv",
          "args": [
            "run",
            "/absolute/path/to/ys-requirements-list/mcp/guides_mcp_server.py"
          ]
       }
     }
   }
   ```

3. **Update Path:** Replace `/absolute/path/to/` with your actual repository location

4. **Restart Claude Desktop**

## Development & Testing

### Using MCP Inspector

Test your server interactively with the built-in MCP Inspector:

```bash
cd /path/to/ys-requirements-list
```bash
uv run mcp dev mcp/guides_mcp_server.py
```
```

The inspector provides a web UI to test each tool with sample inputs.

### Direct Execution

Run the server in stdio mode (for debugging or custom clients):

```bash
cd /path/to/ys-requirements-list
uv run guides_mcp_server.py
```

**Note:** All `uv run` commands automatically handle dependency installation via PEP 723 inline script metadata. No virtual environment setup or `pip install` needed!

## Available Tools

Once configured, you'll have access to these tools:

### 1. `list_guide_divisions`
Lists all divisions (PM, QA, SE, EXD) with guide counts.

**Example:**
```
Can you list all the guide divisions?
```

### 2. `list_guides_by_division`
Lists all guides in a specific division.

**Parameters:**
- `division` (string): pm, qa, se, or exd

**Example:**
```
Show me all the software engineering guides
```

### 3. `get_guide_content`
Retrieves the full content of a specific guide.

**Parameters:**
- `path` (string): Relative path like "se/authentication-module---introduction-1/index.md"

**Example:**
```
Get the authentication module introduction guide for software engineers
```

### 4. `search_guides`
Semantic search across all guides using AI embeddings.

**Parameters:**
- `query` (string): Natural language search query
- `top_k` (integer, optional): Number of results (default: 3, max: 10)

**Example:**
```
Search for guides about user authentication and OAuth
```

### 5. `get_guide_recommendations`
Get personalized guide recommendations.

**Parameters:**
- `topics` (array): List of topics ["auth", "security"]
- `maturity_level` (string, optional): "Introduction 1", "Growth 1", etc.
- `division` (string, optional): pm, qa, se, or exd

**Example:**
```
Recommend guides about authentication and security at the Introduction 1 level for software engineers
```

## Usage Examples

### In Claude Desktop

Once configured, you can ask Claude:

- **"What guide divisions are available?"**
  → Calls `list_guide_divisions`

- **"Show me all SE guides"**
  → Calls `list_guides_by_division` with division="se"

- **"Search for authentication guides"**
  → Calls `search_guides` with query="authentication"

- **"Recommend payment guides at Introduction 1 level"**
  → Calls `get_guide_recommendations` with topics=["payment"], maturity_level="Introduction 1"

Claude automatically selects and executes the appropriate tools.

### Verification

Check that tools are loaded:

1. Look for the 🔧 "Search and tools" icon in Claude Desktop
2. You should see "Implementation Guides" listed
3. 5 tools should be available

## Troubleshooting

### "Command not found" error

Ensure Python is in your PATH:
```bash
which python3
```

Update the config with the full path to Python if needed.

### Authentication errors

Verify your gcloud authentication:
```bash
gcloud auth login
gcloud auth print-identity-token
```

### Connection timeout

The Cloud Run service may take a few seconds to cold start. Wait and retry.

### Tool calls not working

Check the Claude Desktop logs:
- **macOS:** `~/Library/Logs/Claude/mcp*.log`
- **Windows:** `%APPDATA%\Claude\logs\mcp*.log`

## Direct API Access (Alternative)

If MCP setup doesn't work, you can still use the REST API directly:

```bash
# Get auth token
TOKEN=$(gcloud auth print-identity-token)

# Search guides
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

## Architecture

```
┌─────────────────┐
│  Claude / VS    │
│     Code        │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ▼
┌─────────────────┐
│  Local MCP      │
│    Server       │
│ (Python Script) │
└────────┬────────┘
         │ HTTPS + OAuth
         ▼
┌─────────────────┐
│   Cloud Run     │
│   REST API      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vertex AI +    │
│   Firestore     │
└─────────────────┘
```

The MCP server acts as a local bridge, translating MCP protocol calls into REST API requests with proper authentication.

## Security Notes

- Authentication uses your personal gcloud credentials
- The wrapper runs locally on your machine
- No credentials are stored in configuration files
- API calls are authenticated via Google Workspace SSO

## Updating

When the API is updated, simply restart Claude Desktop to pick up changes. No local updates needed since the server calls the live API.
