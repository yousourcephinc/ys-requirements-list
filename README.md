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

## Guides REST API

This repository includes a REST API server that exposes endpoints to interact with the guides.

### Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Running the Server Locally

Start the API server:

```bash
python guides_mcp_api.py
```

The server will start on `http://localhost:8080`

### Testing

You can test the API functionality by running:

```bash
pip install requests  # Install requests library for testing
python test_guides_api.py
```

Or test a deployed server:

```bash
python test_guides_api.py https://your-cloud-run-url.run.app
```

### Available Endpoints

The API provides the following endpoints:

- **GET /divisions**: List all divisions (categories) of guides
- **GET /divisions/{division}/guides**: List all guides in a specific division
- **GET /guides/{path}**: Get the content of a specific guide
- **POST /search**: Search guides using semantic search (body: `{"query": "...", "top_k": 5}`)
- **POST /rebuild-index**: Rebuild the semantic search index
- **POST /recommendations**: Get guide recommendations (body: `{"topics": [...], "maturity_level": "...", "division": "..."}`)
- **GET /health**: Health check endpoint

### Deploying to Google Cloud Run

See the deployment guide in the repository for instructions on deploying to GCP Cloud Run. 
