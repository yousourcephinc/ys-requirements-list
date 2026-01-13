# GitHub Copilot Instructions for Implementation Guides

## Project Overview

This is a **dual-purpose implementation guides platform** that serves as both a repository of engineering best practices and a Model Context Protocol (MCP) server. The architecture combines content stored as Markdown files with a cloud-hosted API that provides semantic search and integration with GitHub Copilot.

## Core Architecture

### Service Boundaries
- **Content Layer**: Markdown guides organized by division (`se/`, `pm/`, `qa/`, `exd/`) and maturity level
- **MCP Server**: Unified Flask app (`mcp/guides_mcp_http_server.py`) serving both REST API and MCP endpoints
- **Semantic Search**: Google Vertex AI embeddings with Firestore storage, graceful fallback to text search
- **Content Pipeline**: Daily Notion sync via GitHub Actions -> Markdown files -> Vector embeddings

### Key Integration Points
- **VS Code MCP**: Configured in `.vscode/settings.json` with hardcoded `test-key` for Copilot compatibility
- **Cloud Run**: Auto-deployment from `main` branch, scales 0-5 instances
- **Authentication**: Google OAuth for users, static API key for tools, no local auth required

## Critical Developer Workflows

### Local Development Server
```bash
# Start unified server (REST API + MCP on port 8080)
cd mcp && python guides_mcp_http_server.py
```

### Content Management
```bash
# Sync from Notion (requires NOTION_API_KEY in .env)
make sync

# Test MCP server locally
make test-mcp
```

### Deployment Pipeline
- Push to `main` -> Automatic Cloud Run deployment via GitHub Actions
- Content updates -> Auto-sync from Notion daily at 2 AM UTC
- No manual deployment steps required

## GitHub Copilot MCP Integration

**Available MCP Tools** (auto-configured in `.vscode/settings.json`):
- `list_guide_divisions` - List all divisions (PM, QA, SE, EXD) with guide counts
- `list_guides_by_division` - List all guides in a specific division
- `get_guide_content` - Get full guide content with requirements and metadata
- `search_guides` - Semantic search using AI embeddings
- `get_guide_recommendations` - Get personalized guide recommendations

**Example Usage:**
```
User: @workspace Search for authentication guides
Copilot: [Calls search_guides("authentication")] 
Returns relevant guides with similarity scores
```

## Quick API Reference

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
