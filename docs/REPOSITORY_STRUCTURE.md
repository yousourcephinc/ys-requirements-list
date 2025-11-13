# Repository Structure

This document describes the organization of files in the ys-requirements-list repository.

## Directory Layout

```
ys-requirements-list/
├── .github/              # GitHub configuration
│   ├── workflows/        # CI/CD workflows
│   └── copilot-instructions.md  # GitHub Copilot instructions
├── docs/                 # Documentation
│   ├── README_MCP.md     # MCP server documentation
│   ├── MCP_SETUP.md      # MCP setup guide
│   ├── SETUP_GUIDE.md    # General setup guide
│   ├── DEPLOYMENT.md     # Deployment instructions
│   └── REPOSITORY_STRUCTURE.md  # This file
├── mcp/                  # MCP server implementations
│   ├── guides_mcp_server.py        # FastMCP stdio server (PEP 723, for Claude Desktop)
│   ├── guides_mcp_http_server.py   # Flask HTTP server (Cloud Run + GitHub Copilot)
│   ├── guides_mcp_stdio_proxy.py   # Stdio proxy (connects to HTTP server)
│   ├── guides_mcp.py               # Legacy MCP implementation
│   ├── setup_mcp.py                # MCP setup utility
│   └── test_minimal.py             # Minimal MCP test
├── scripts/              # Utility scripts
│   ├── sync_notion.py    # Notion synchronization
│   └── vector_search.py  # Semantic search with Vertex AI
├── tests/                # Test files
│   ├── test_guides_api.py
│   ├── test_guides_mcp.py
│   ├── test_notion_connection.py
│   └── test_semantic_search.py
├── guides/               # Implementation guides content
│   ├── pm/               # Product Management
│   ├── qa/               # Quality Assurance
│   ├── se/               # Software Engineering
│   ├── exd/              # Experience Design
│   └── semantic_index/   # Vector embeddings (gitignored)
├── README.md             # Main project README
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Python project configuration
├── Makefile              # Build automation
├── Dockerfile            # Cloud Run container
└── .gitignore            # Git ignore rules
```

## File Purposes

### MCP Servers

- **guides_mcp_http_server.py**: Unified Flask HTTP server
  - Serves both REST API and MCP endpoints
  - Deployed on Google Cloud Run (production)
  - Runs locally for GitHub Copilot integration
  - Integrates with Vertex AI and Firestore
  - Authentication via Google Cloud identity tokens

- **guides_mcp_server.py**: FastMCP stdio server (PEP 723)
  - Recommended for Claude Desktop integration
  - Zero-installation with `uv run`
  - Connects to Cloud Run HTTP server via proxy

- **guides_mcp_stdio_proxy.py**: Stdio-to-HTTP proxy
  - Bridges stdio MCP protocol to HTTP server
  - Used by guides_mcp_server.py to connect to Cloud Run
  - Handles authentication and request translation

- **guides_mcp.py**: Legacy MCP implementation
  - Direct file system access
  - Not actively maintained

### Scripts

- **sync_notion.py**: Synchronizes implementation guides from Notion
  - Runs daily via GitHub Actions
  - Updates `guides/` directory
  - Preserves local-only guides (no source_url)

- **generate_embeddings.py**: Generate vector embeddings for guides
  - Uses Vertex AI textembedding-gecko@003
  - Stores embeddings in Firestore
  - Runs after Notion sync

- **vector_search.py**: Semantic search implementation
  - Uses Vertex AI embeddings
  - Stores vectors in Firestore
  - Graceful fallback to text search

- **onboard_guide.py**: Onboard standalone guides to the collection
  - Adds frontmatter metadata
  - Creates proper directory structure
  - Marks as local-only (no Notion source)

- **upload_foundational_to_notion.py**: Upload foundational guides to Notion
  - Bulk upload guides to Notion database
  - Preserves frontmatter metadata

### Documentation

- **README_MCP.md**: Comprehensive MCP server documentation
- **MCP_SETUP.md**: Step-by-step setup instructions
- **SETUP_GUIDE.md**: General project setup
- **DEPLOYMENT.md**: Cloud deployment guide
- **COPILOT_SETUP.md**: GitHub Copilot MCP integration
- **api-reference.md**: REST API endpoint documentation
- **local-development.md**: Local development guide
- **troubleshooting.md**: Common issues and solutions
- **scripts.md**: Script usage documentation
- **testing.md**: Testing guide
- **configuration.md**: Environment variables and configuration

## Import Paths

Due to the reorganization, import statements in code need to reference the correct paths:

### For files in `mcp/`:
```python
# Add scripts directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from sync_notion import search_semantic_index
from vector_search import search_guides
```

### For files in `tests/`:
```python
# Add scripts directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from sync_notion import search_semantic_index
```

## Running Commands

All commands should be run from the repository root:

```bash
# MCP server installation
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"

# MCP development mode
uv run mcp dev mcp/guides_mcp_server.py

# Sync guides from Notion
python scripts/sync_notion.py

# Run HTTP server locally (REST API + MCP)
python mcp/guides_mcp_http_server.py

# Run tests
python tests/test_guides_api.py

# Using Makefile
make sync        # Sync from Notion
make mcp         # Run alternative MCP server
make test-mcp    # Test MCP server
```

## Development Workflow

1. **Adding new guides**: 
   - Automatic: Synced from Notion daily via GitHub Actions
   - Manual: Use `scripts/onboard_guide.py` for local-only guides
2. **Testing MCP server**:
   - Claude Desktop: `uv run mcp dev mcp/guides_mcp_server.py`
   - GitHub Copilot: `python mcp/guides_mcp_http_server.py` (HTTP mode)
3. **Testing API**: Use `python mcp/guides_mcp_http_server.py` for local testing
4. **Running tests**: Execute test files from the repository root with `pytest`
5. **Deployment**: Push to main branch triggers automatic Cloud Run deployment

## .gitignore Coverage

The `.gitignore` file now includes comprehensive coverage for:

- Python artifacts (`__pycache__/`, `*.pyc`, `dist/`, etc.)
- Virtual environments (`.venv/`, `venv/`, etc.)
- IDEs (`.vscode/`, `.idea/`, etc.)
- OS files (`.DS_Store`, `Thumbs.db`)
- Development temp files (`tmp/`, `temp/`, `logs/`, etc.)
- Database files (`*.db`, `*.sqlite`)
- Large binary files (`guides/semantic_index/`)
- Custom scratch directories (`scratch/`, `playground/`)

## Related Documentation

- [Main README](../README.md) - Project overview and quick start
- [API Reference](api-reference.md) - REST API documentation
- [Local Development](local-development.md) - Setup and development guide
- [Configuration](configuration.md) - Environment variables and settings
- [Scripts](scripts.md) - Script usage and automation
- [Testing](testing.md) - Testing guide
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [MCP Setup](MCP_SETUP.md) - MCP server setup
- [Deployment](DEPLOYMENT.md) - Cloud deployment guide
