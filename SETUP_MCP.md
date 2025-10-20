# Guides MCP Server Setup Guide

This document provides detailed instructions for setting up and running the Guides MCP (Model Context Protocol) server.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Access to the guides repository data

## Installation

### 1. Setup Python Environment

It's recommended to use a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

You can install all required dependencies using the setup script:

```bash
python setup_mcp.py
```

Or manually with pip:

```bash
pip install -r requirements.txt
```

## Configuration

The MCP server will use the same configuration as the Notion sync script. If you haven't set it up yet:

1. Create a `.env` file with these variables:

```
NOTION_API_KEY="secret_..."
NOTION_DATABASE_ID="..."
```

2. Make sure you have run the sync script at least once to create the guides directory:

```bash
python sync_notion.py
```

## Running the MCP Server

### Start the Server

You can start the server using one of these methods:

```bash
# Direct method
python guides_mcp.py

# Using make
make mcp
```

The server will run on localhost port 8080 by default.

### Test the Server

To test if the server is running correctly:

```bash
# Direct method
python test_guides_mcp.py

# Using make
make test-mcp
```

This will perform a series of tests to verify the functionality of all tools provided by the MCP server.

## Using the MCP Server

The MCP server exposes several tools to interact with the guides:

### Available Tools

- **list_guide_divisions**
  - Lists all divisions (categories) of guides
  - No parameters required

- **list_guides_by_division**
  - Lists all guides in a specific division
  - Parameters:
    - `division` (string): The division name

- **get_guide_content**
  - Gets the content of a specific guide
  - Parameters:
    - `guide_path` (string): Relative path to the guide index file

- **search_guides**
  - Searches guides using semantic search
  - Parameters:
    - `query` (string): The search query
    - `top_k` (integer, optional): Maximum number of results to return (default: 5)

- **rebuild_semantic_index**
  - Rebuilds the semantic search index for guides
  - No parameters required

- **get_guide_recommendations**
  - Gets guide recommendations based on topics and filters
  - Parameters:
    - `topics` (array of strings): List of topics of interest
    - `maturity_level` (string, optional): Filter by maturity level
    - `division` (string, optional): Filter by division

### Using with MCP Client

Here's an example of how to use the MCP client to interact with the server:

```python
import asyncio
from mcp import MCPClient

async def main():
    # Connect to the server
    client = MCPClient(port=8080)
    
    # Get service info
    service_info = await client.get_service_info()
    print(f"Connected to {service_info.name} v{service_info.version}")
    
    # List divisions
    divisions = await client.call_tool("list_guide_divisions", {})
    print(f"Found {len(divisions.result)} divisions")
    
    # Search for guides
    search_results = await client.call_tool(
        "search_guides", 
        {"query": "authentication"}
    )
    
    for result in search_results.result:
        print(f"{result['title']} (Score: {result['score']:.3f})")

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **Server fails to start**
   - Check if the required ports are available
   - Verify that all dependencies are installed correctly
   - Ensure the guides directory exists and has been populated

2. **Semantic search not working**
   - Run the `rebuild_semantic_index` tool to regenerate the index
   - Check if the guides directory contains valid content

3. **MCP client connection error**
   - Ensure the MCP server is running
   - Verify you're using the correct port

For any other issues, check the server logs for detailed error messages.