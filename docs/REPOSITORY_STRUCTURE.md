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
│   ├── guides_mcp_server.py     # FastMCP server (PEP 723, recommended)
│   ├── guides_mcp_api.py        # Cloud Run REST API
│   ├── guides_mcp.py            # Alternative MCP implementation
│   └── setup_mcp.py             # MCP setup utility
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

- **guides_mcp_server.py**: FastMCP-based MCP server using PEP 723 inline dependencies
  - Recommended for Claude Desktop integration
  - Zero-installation with `uv run`
  - Connects to Cloud Run API

- **guides_mcp_api.py**: Flask REST API deployed on Cloud Run
  - Provides HTTP endpoints for guide access
  - Integrates with Vertex AI and Firestore
  - Authentication via Google Cloud

- **guides_mcp.py**: Alternative MCP implementation
  - Direct file system access
  - Legacy implementation

### Scripts

- **sync_notion.py**: Synchronizes implementation guides from Notion
  - Runs daily via GitHub Actions
  - Updates `guides/` directory

- **vector_search.py**: Semantic search implementation
  - Uses Vertex AI embeddings
  - Stores vectors in Firestore

### Documentation

- **README_MCP.md**: Comprehensive MCP server documentation
- **MCP_SETUP.md**: Step-by-step setup instructions
- **SETUP_GUIDE.md**: General project setup
- **DEPLOYMENT.md**: Cloud deployment guide

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

# Run API locally
python mcp/guides_mcp_api.py

# Run tests
python tests/test_guides_api.py

# Using Makefile
make sync        # Sync from Notion
make mcp         # Run alternative MCP server
make test-mcp    # Test MCP server
```

## Development Workflow

1. **Adding new guides**: Guides are synced from Notion automatically
2. **Testing MCP server**: Use `uv run mcp dev mcp/guides_mcp_server.py`
3. **Testing API**: Use `python mcp/guides_mcp_api.py` for local testing
4. **Running tests**: Execute test files from the repository root
5. **Deployment**: Push to main branch triggers Cloud Run deployment

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

## Migration Notes

This repository was reorganized on 2024-10-21 to improve structure and maintainability. Key changes:

1. Created logical directory structure (mcp/, scripts/, tests/, docs/)
2. Updated all import paths to reflect new organization
3. Updated documentation references to new file locations
4. Updated CI/CD workflows and build files
5. Enhanced .gitignore with comprehensive development patterns

All functionality remains the same; only file locations have changed.
