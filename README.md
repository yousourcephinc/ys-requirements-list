# ys-requirements-list
Repository of requirements list, implementation guides organized by software modules and maturity levels.

## Notion Sync

This repository includes a helper script to sync guides from a Notion database into a `guides/` folder.

1. Create a `.env` file with these variables:

```
NOTION_API_KEY="secret_..."
NOTION_DATABASE_ID="..."
```

2. Install deps and run:

```bash
pip install -r requirements.txt
python sync_notion.py
```

The script will create a `guides/` directory with one subfolder per module and guide.

## MCP Server

This repository includes a Model Context Protocol (MCP) server that exposes tools to interact with the guides.

### Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Running the Server

Start the MCP server:

```bash
python guides_mcp.py
```

Or use the make target:

```bash
make mcp
```

### Testing

You can test the MCP server functionality by running:

```bash
python test_guides_mcp.py
```

Or use the make target:

```bash
make test-mcp
```

### Available Tools

The MCP server provides the following tools:

- **list_guide_divisions**: List all divisions (categories) of guides
- **list_guides_by_division**: List all guides in a specific division
- **get_guide_content**: Get the content of a specific guide
- **search_guides**: Search guides using semantic search
- **rebuild_semantic_index**: Rebuild the semantic search index
- **get_guide_recommendations**: Get guide recommendations based on topics and filters 
