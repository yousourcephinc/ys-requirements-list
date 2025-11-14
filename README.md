# Implementation Guides Repository

> **Dual-purpose platform**: Engineering best practices repository + Model Context Protocol (MCP) server for AI coding assistants

[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-blue)](https://mcp-server-375955300575.us-central1.run.app)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io)

## Overview

This repository serves dual purposes:

1. **Content Repository**: 130+ implementation guides covering Software Engineering (SE), Experience Design (EXD), Product Management (PM), and Quality Assurance (QA) best practices
2. **MCP Server**: AI-powered semantic search API that integrates with GitHub Copilot and other AI coding assistants

### Key Features

- 🔍 **Semantic Search**: AI-powered guide discovery using Google Vertex AI embeddings
- 🎯 **Division Filtering**: Guides organized by SE, EXD, PM, QA divisions
- 📊 **Maturity Levels**: Foundational to decline-stage guidance for different product lifecycles
- 🔐 **Secure API**: Google Cloud authentication with domain-based access control
- 🤖 **MCP Integration**: Native support for GitHub Copilot and Claude Desktop
- 📝 **Auto-Sync**: Daily synchronization from Notion CMS

## Quick Start

### For GitHub Copilot (Primary)

The easiest way to use implementation guides with GitHub Copilot:

**Option 1: Using specify CLI (Recommended)**
```bash
# Initialize a new project with Copilot integration
specify init --ai copilot --script sh

# This auto-creates .vscode/settings.json with MCP configuration
```

**Option 2: Manual Setup**

1. **Authenticate with Google Cloud**:
```bash
gcloud auth login
```

2. **Start the local MCP server**:
```bash
cd ~/code/ys-requirements-list
python mcp/guides_mcp_http_server.py
# Server runs on http://localhost:8080
```

3. **Add to your `.vscode/settings.json`**:
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

4. **Use in Copilot Chat**:
```
@workspace Search for authentication guides
@workspace Show me all SE guides
@workspace Recommend payment module guides
```

**Full Setup Guide**: [docs/COPILOT_SETUP.md](docs/COPILOT_SETUP.md)

### For Claude Desktop

```bash
cd /path/to/ys-requirements-list
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"
```

**Full Setup Guide**: [docs/MCP_SETUP.md](docs/MCP_SETUP.md)

### For API Users

```bash
# Get authentication token
TOKEN=$(gcloud auth print-identity-token)

# Search for guides
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication OAuth", "top_k": 5}' \
  https://mcp-server-375955300575.us-central1.run.app/search

# List all divisions
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions

# Get guide content
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/guides/se/authentication-module---introduction-1/index.md
```

### For Local Development

```bash
# Clone repository
git clone https://github.com/yousourcephinc/ys-requirements-list.git
cd ys-requirements-list

# Install dependencies
pip install -r requirements.txt

# Run MCP server locally
cd mcp && python guides_mcp_http_server.py

# Server runs on http://localhost:8080
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Content Pipeline                         │
│                                                             │
│  Notion CMS ──daily sync──> GitHub ──auto deploy──>        │
│                              │                              │
│                              ├──> Vector Embeddings         │
│                              │    (Vertex AI)               │
│                              │                              │
│                              └──> Firestore                 │
│                                   (Semantic Index)          │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (Cloud Run)                   │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐   ┌──────────────┐   │
│  │  REST API   │───▶│ Semantic     │──▶│  Firestore   │   │
│  │  Endpoints  │    │ Search       │   │  Vector DB   │   │
│  └─────────────┘    └──────────────┘   └──────────────┘   │
│         │                                                   │
│         └──────────▶ MCP Protocol Handler                  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Coding Assistants                     │
│                                                             │
│  • GitHub Copilot (VS Code)                                │
│  • Claude Desktop                                           │
│  • Other MCP-compatible tools                              │
└─────────────────────────────────────────────────────────────┘
```

## Documentation

- **[MCP Setup Guide](docs/MCP_SETUP.md)** - Configure MCP server for Claude Desktop
- **[GitHub Copilot Setup](docs/COPILOT_SETUP.md)** - Configure for VS Code
- **[API Reference](docs/api-reference.md)** - REST API endpoints and examples
- **[Local Development](docs/local-development.md)** - Setup local development environment
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Cloud Run deployment instructions
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Testing Guide](docs/testing.md)** - How to run and write tests
- **[Configuration Reference](docs/configuration.md)** - Environment variables and settings

## Project Structure

```
ys-requirements-list/
├── guides/                   # Implementation guides (130+ markdown files)
│   ├── se/                  # Software Engineering
│   ├── exd/                 # Experience Design
│   ├── pm/                  # Product Management
│   └── qa/                  # Quality Assurance
├── mcp/                     # MCP server implementations
│   ├── guides_mcp_http_server.py    # Main HTTP server (Flask + MCP)
│   ├── guides_mcp_stdio_proxy.py    # stdio proxy for Claude Desktop
│   └── guides_mcp.py                # Alternative implementation
├── scripts/                 # Utility scripts
│   ├── sync_notion.py       # Daily Notion sync
│   ├── generate_embeddings.py       # Vector embedding generation
│   ├── vector_search.py     # Semantic search implementation
│   └── onboard_guide.py     # Add new guides
├── tests/                   # Test suite
├── docs/                    # Documentation
└── .github/workflows/       # CI/CD automation
```

## Available MCP Tools

The MCP server provides 5 tools for AI assistants:

1. **`list_guide_divisions`** - List all divisions (SE, PM, QA, EXD)
2. **`list_guides_by_division`** - List all guides in a specific division
3. **`get_guide_content`** - Get full guide content with requirements
4. **`search_guides`** - Semantic search using AI embeddings
5. **`get_guide_recommendations`** - Get personalized guide recommendations

## Content Statistics

- **130+ Implementation Guides** across 4 divisions
- **SE (Software Engineering)**: 70+ guides
- **EXD (Experience Design)**: 25+ guides
- **PM (Product Management)**: 20+ guides
- **QA (Quality Assurance)**: 15+ guides

### Maturity Levels

- Foundational (core concepts)
- Introduction 1 & 2 (getting started)
- Growth 1 & 2 (scaling)
- Maturity 1 & 2 (optimization)
- Decline 1 & 2 (sunset planning)

## Contributing

### Adding New Guides

Use the onboarding script to add new implementation guides:

```bash
# Single file
python scripts/onboard_guide.py path/to/guide.md

# Directory of files
python scripts/onboard_guide.py path/to/guides/

# The script will prompt for:
# - Division (SE, EXD, PM, QA)
# - Maturity level
# - Guide title
```

### Syncing from Notion

Guides are automatically synced from Notion daily. For manual sync:

```bash
# Requires NOTION_API_KEY in .env
python scripts/sync_notion.py
```

## Deployment

The MCP server auto-deploys to Google Cloud Run on push to `main` branch.

**Manual deployment**:
```bash
make deploy
```

**Cost**: ~$20/month (Cloud Run + Vertex AI + Firestore)

## Authentication

### For API Access
- **Google OAuth**: Use `gcloud auth print-identity-token`
- **API Key**: Set `IMPLEMENTATION_GUIDES_API_KEY` for tools

### For MCP Tools
- **Local**: Uses `gcloud` authentication automatically
- **Cloud**: Domain-based authentication for `@you-source.com`

## Support

- **Issues**: [GitHub Issues](https://github.com/yousourcephinc/ys-requirements-list/issues)
- **Documentation**: See [docs/](docs/) folder
- **Troubleshooting**: See [docs/troubleshooting.md](docs/troubleshooting.md)

## License

Copyright © 2024 YourSource Philippines Inc.

---

**Last Updated**: November 13, 2025
