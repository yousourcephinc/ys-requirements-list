# Local Development Guide

This guide covers setting up and running the Implementation Guides MCP server locally for development and testing.

## Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`
- `gcloud` CLI (for authentication)
- Git

### Install uv (Recommended)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install gcloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Linux/Windows
# See: https://cloud.google.com/sdk/docs/install
```

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/yousourcephinc/ys-requirements-list.git
cd ys-requirements-list
```

### 2. Install Dependencies

**Using uv** (recommended):
```bash
uv pip install -r requirements.txt
```

**Using pip**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Authentication

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project implementation-guides-439017
```

### 4. Set Environment Variables

Create `.env` file in the repository root:

```bash
# Required for Notion sync (optional for local development)
NOTION_API_KEY=your_notion_api_key

# Required for semantic search
GOOGLE_CLOUD_PROJECT=implementation-guides-439017
FIRESTORE_DATABASE=implementation-guides

# Optional: API key for MCP tools
IMPLEMENTATION_GUIDES_API_KEY=test-key
```

## Running Locally

### Option 1: HTTP Server (REST API + MCP)

The main server provides both REST API and MCP protocol endpoints.

```bash
# From repository root
cd mcp
python guides_mcp_http_server.py
```

Server runs on `http://localhost:8080`

**Test it**:
```bash
# Health check
curl http://localhost:8080/

# List divisions
curl http://localhost:8080/divisions

# Search guides
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}' \
  http://localhost:8080/search
```

### Option 2: stdio Proxy (For Claude Desktop)

The stdio proxy connects to the HTTP server via MCP protocol.

```bash
# Terminal 1: Start HTTP server
cd mcp
python guides_mcp_http_server.py

# Terminal 2: Start stdio proxy
uv run mcp/guides_mcp_stdio_proxy.py
```

### Option 3: Development Mode (FastMCP)

Use FastMCP's development mode for automatic reloading:

```bash
uv run mcp dev mcp/guides_mcp_server.py
```

## Project Structure

```
ys-requirements-list/
├── mcp/
│   ├── guides_mcp_http_server.py  # Main HTTP server (Flask)
│   ├── guides_mcp_stdio_proxy.py  # stdio proxy for Claude Desktop
│   ├── guides_mcp.py              # Alternative implementation
│   └── setup_mcp.py               # Setup utilities
├── scripts/
│   ├── sync_notion.py             # Notion synchronization
│   ├── generate_embeddings.py     # Vector embeddings
│   ├── vector_search.py           # Semantic search
│   └── onboard_guide.py           # Add new guides
├── tests/
│   ├── test_guides_api.py         # API tests
│   ├── test_guides_mcp.py         # MCP tests
│   ├── test_notion_connection.py  # Notion tests
│   └── test_semantic_search.py    # Search tests
└── guides/                        # Implementation guides
    ├── se/                        # Software Engineering
    ├── exd/                       # Experience Design
    ├── pm/                        # Product Management
    └── qa/                        # Quality Assurance
```

## Development Workflows

### Adding New Guides

```bash
# Single guide
python scripts/onboard_guide.py path/to/guide.md

# Multiple guides from directory
python scripts/onboard_guide.py path/to/guides/
```

The script will prompt for:
- Division (SE, EXD, PM, QA)
- Maturity level
- Guide title

### Syncing from Notion

```bash
# Requires NOTION_API_KEY in .env
python scripts/sync_notion.py
```

### Generating Vector Embeddings

```bash
# Generate embeddings for new guides
python scripts/generate_embeddings.py

# Rebuild entire index (expensive!)
python scripts/generate_embeddings.py --rebuild
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_guides_api.py

# Run with coverage
pytest --cov=mcp --cov=scripts

# Run with verbose output
pytest -v
```

## Testing the MCP Server

### Testing HTTP Server

```bash
# Start server
cd mcp && python guides_mcp_http_server.py

# In another terminal:

# Get authentication token
TOKEN=$(gcloud auth print-identity-token)

# List divisions
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/divisions | jq

# Search guides
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication OAuth", "top_k": 5}' \
  http://localhost:8080/search | jq

# Get guide content
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/guides/se/authentication-module---introduction-1/index.md | jq
```

### Testing MCP Protocol

```bash
# Use MCP inspector
uv run mcp dev mcp/guides_mcp_server.py

# Or test with Claude Desktop by updating config:
# ~/.config/Claude/claude_desktop_config.json
```

### Testing with GitHub Copilot

1. Create test project:
```bash
mkdir test-project
cd test-project
specify init --here --ai copilot --no-git --force
```

2. Open in VS Code

3. Verify `.vscode/settings.json` has:
```json
{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": {
    "implementation-guides": {
      "type": "http",
      "url": "http://127.0.0.1:8080/mcp"
    }
  }
}
```

4. Start local server:
```bash
cd /path/to/ys-requirements-list/mcp
python guides_mcp_http_server.py
```

5. Test in Copilot Chat:
```
Search for authentication guides
```

## Debugging

### Enable Debug Logging

```python
# Add to top of guides_mcp_http_server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Server Logs

```bash
# Server logs to stdout
tail -f mcp_server.log  # if logging to file
```

### Verify Firestore Connection

```python
# Test script
python -c "
from google.cloud import firestore
db = firestore.Client(database='implementation-guides')
docs = list(db.collection('guides').limit(1).stream())
print(f'Connected! Found {len(docs)} document(s)')
"
```

### Verify Vertex AI Access

```python
# Test script
python scripts/vector_search.py
```

### Common Issues

**Import errors**:
```bash
# Ensure you're in the right directory
cd /path/to/ys-requirements-list

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

**Authentication errors**:
```bash
# Re-authenticate
gcloud auth application-default login
gcloud auth login
```

**Port already in use**:
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use different port
PORT=8081 python mcp/guides_mcp_http_server.py
```

## Hot Reloading

For faster development, use auto-reload:

```bash
# Install watchdog
uv pip install watchdog

# Run with auto-reload
uvicorn mcp.guides_mcp_http_server:app --reload --port 8080
```

## Code Quality

### Linting

```bash
# Install ruff
uv pip install ruff

# Run linter
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Type Checking

```bash
# Install mypy
uv pip install mypy

# Run type checker
mypy mcp/ scripts/
```

### Formatting

```bash
# Install black
uv pip install black

# Format code
black mcp/ scripts/ tests/
```

## Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NOTION_API_KEY` | For sync | Notion API integration key | - |
| `GOOGLE_CLOUD_PROJECT` | Yes | GCP project ID | `implementation-guides-439017` |
| `FIRESTORE_DATABASE` | Yes | Firestore database name | `implementation-guides` |
| `IMPLEMENTATION_GUIDES_API_KEY` | For tools | Static API key for MCP tools | `test-key` |
| `PORT` | No | Server port | `8080` |
| `DEBUG` | No | Enable debug logging | `false` |

## Next Steps

- **[API Reference](api-reference.md)** - Learn about available endpoints
- **[Testing Guide](testing.md)** - Write and run tests
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to Cloud Run
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Support

- **Issues**: [GitHub Issues](https://github.com/yousourcephinc/ys-requirements-list/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yousourcephinc/ys-requirements-list/discussions)

---

**Last Updated**: November 13, 2025
