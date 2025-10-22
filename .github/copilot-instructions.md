# GitHub Copilot Instructions for Guides API

## MCP Server Available

This workspace includes an MCP server (`guides_mcp_server.py`) built with FastMCP that provides access to implementation guides through the Model Context Protocol.

**Installation Pattern:**
```bash
# Authenticate first
gcloud auth login

# Install to Claude Desktop (zero manual setup)
cd /path/to/ys-requirements-list
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"
```

**Key Features:**
- ✅ **PEP 723 Inline Dependencies** - No manual `pip install` needed
- ✅ **FastMCP Framework** - Uses official MCP Python SDK
- ✅ **5 AI Tools** - Search, browse, and get recommendations
- ✅ **Google Cloud Auth** - Leverages your gcloud credentials

Dependencies (`mcp>=1.2.0`, `httpx>=0.27.0`) are automatically installed by `uv run`.

## Available Implementation Guides API

This workspace has access to a REST API containing implementation guides for software modules across different maturity levels.

**API Endpoint:** `https://mcp-server-375955300575.us-central1.run.app`

**Authentication:** Requires Google Workspace authentication
```bash
TOKEN=$(gcloud auth print-identity-token)
```

## Available Endpoints

### List Divisions
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions
```

Returns: `[{"name": "se", "guide_count": 70}, ...]`

### List Guides in Division
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions/se/guides
```

Returns: Array of guides with title, maturity, path

### Get Guide Content
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/guides/se/authentication-module---introduction-1/index.md
```

Returns: Full guide content with metadata

### Semantic Search
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "user authentication OAuth", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

Returns: Relevant guides with similarity scores

### Get Recommendations
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topics": ["authentication", "security"], "maturity_level": "Introduction 1", "division": "se"}' \
  https://mcp-server-375955300575.us-central1.run.app/recommendations
```

Returns: Top 5 recommended guides

## Guide Structure

- **Divisions:** pm (Product Management), qa (Quality Assurance), se (Software Engineering), exd (Experience Design)
- **Maturity Levels:** Introduction 1, Introduction 2, Growth 1, Growth 2, etc.
- **Content:** Markdown files with functional requirements, security requirements, architectural patterns, checklists

## Usage in Code Generation

When generating code for common modules (auth, payments, user management, etc.), you can reference or fetch relevant implementation guides to ensure best practices.

Example usage:
```python
import subprocess
import json
import requests

def get_auth_token():
    result = subprocess.run(['gcloud', 'auth', 'print-identity-token'], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def search_guides(query):
    token = get_auth_token()
    response = requests.post(
        'https://mcp-server-375955300575.us-central1.run.app/search',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'query': query, 'top_k': 3}
    )
    return response.json()

# Search for authentication guides
guides = search_guides("OAuth authentication setup")
for guide in guides:
    print(f"{guide['title']} - Score: {guide['score']:.2f}")
```

## When to Reference Guides

- Implementing authentication/authorization
- Setting up payment processing
- Building user management systems
- Creating notification systems
- Implementing search functionality
- Setting up file upload/download
- Configuring settings and preferences
- Adding third-party API integrations

## Quick Reference Commands

```bash
# List all divisions
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/divisions | jq

# Search for guides
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"query": "your search here", "top_k": 5}' \
  https://mcp-server-375955300575.us-central1.run.app/search | jq
```
