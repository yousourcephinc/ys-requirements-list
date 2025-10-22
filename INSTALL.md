# Quick Install Guide

## For GitHub Copilot Users (Primary)

The easiest way to use implementation guides is through GitHub Copilot in VS Code.

### Prerequisites
1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth login
   ```

### Setup

**Option 1: Use Workspace Settings (Recommended)**

This repository includes `.vscode/settings.json` with MCP configuration.

1. Open this repository in VS Code
2. Settings are automatically loaded
3. Reload window (Cmd+Shift+P → "Developer: Reload Window")

**Option 2: Manual Configuration**

Add to your VS Code User Settings:

1. Open Settings (Cmd+, or Ctrl+,)
2. Search for "copilot mcp"
3. Edit `settings.json`:
   ```json
   {
     "github.copilot.chat.mcp.servers": {
       "implementation-guides": {
         "command": "uv",
         "args": [
           "--quiet",
           "run",
           "--with",
           "mcp>=1.2.0",
           "--with",
           "httpx>=0.27.0",
           "https://raw.githubusercontent.com/yousourcephinc/ys-requirements-list/main/mcp/guides_mcp_server.py"
         ]
       }
     }
   }
   ```

### Usage

In GitHub Copilot Chat, use `@workspace`:

```
@workspace What guide divisions are available?
@workspace Search for authentication guides
@workspace Recommend payment guides at Introduction 1 level for SE
@workspace Implement user authentication following the guide
```

See [COPILOT_SETUP.md](docs/COPILOT_SETUP.md) for detailed usage examples.

---

## For Claude Desktop Users

Install the MCP server to Claude Desktop:

### Prerequisites
Same as above (uv + gcloud auth)

### Installation

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "implementation-guides": {
      "command": "uv",
      "args": [
        "--quiet",
        "run",
        "--with",
        "mcp>=1.2.0",
        "--with",
        "httpx>=0.27.0",
        "https://raw.githubusercontent.com/yousourcephinc/ys-requirements-list/main/mcp/guides_mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop and ask:
- "What guide divisions are available?"
- "Search for authentication guides"

---

## For API Users

If you prefer REST API:

```bash
TOKEN=$(gcloud auth print-identity-token)

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

---

## Documentation

- [GitHub Copilot Setup](docs/COPILOT_SETUP.md) - Detailed Copilot integration guide
- [Claude Desktop Setup](docs/MCP_SETUP.md) - Claude Desktop installation
- [REST API Documentation](docs/README_MCP.md) - Direct API usage
- [Deployment Guide](docs/DEPLOYMENT.md) - Backend infrastructure

---

## Quick Links

- **API Endpoint:** https://mcp-server-375955300575.us-central1.run.app
- **MCP Server:** [guides_mcp_server.py](mcp/guides_mcp_server.py)
- **Repository:** https://github.com/yousourcephinc/ys-requirements-list
