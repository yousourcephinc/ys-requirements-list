# ys-requirements-list

Repository of implementation guides organized by software modules and maturity levels. Accessible through GitHub Copilot, Claude Desktop, or REST API.

## 🤖 For Developers: GitHub Copilot Integration

**Use implementation guides directly in VS Code with GitHub Copilot!**

This repository includes an MCP (Model Context Protocol) server that connects your guides to GitHub Copilot Chat.

### Quick Setup

1. Install prerequisites:
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Authenticate with Google Cloud
   gcloud auth login
   ```

2. Open this repository in VS Code - settings are pre-configured in `.vscode/settings.json`

3. Reload VS Code (Cmd+Shift+P → "Developer: Reload Window")

4. Use Copilot Chat with `@workspace`:
   ```
   @workspace Search for authentication guides
   @workspace Recommend payment guides at Introduction 1 for SE
   @workspace Implement user management following the guide
   ```

**See [INSTALL.md](INSTALL.md) for detailed setup** | **[Copilot Usage Guide](docs/COPILOT_SETUP.md)**

---

## Architecture

- **Content Storage**: Notion database → GitHub repository
- **MCP Server**: Local Python script (PEP 723, zero-install)
- **API Platform**: Google Cloud Run (serverless, scale-to-zero)
- **Semantic Search**: Google Vertex AI (text-embedding-004) + Firestore vector store
- **Authentication**: Google Workspace SSO (domain:you-source.com)
- **Automation**: GitHub Actions for daily Notion sync
- **AI Integration**: GitHub Copilot + Claude Desktop via MCP

## Notion Sync

This repository includes an automated sync from Notion that runs daily at 2 AM UTC.

### Manual Sync Locally

1. Create a `.env` file:

```bash
NOTION_API_KEY="secret_..."
NOTION_DATABASE_ID="..."
NOTION_VIEW_ID="..."
```

2. Install dependencies and run:

```bash
pip install notion-client python-dotenv
python scripts/sync_notion.py
```

The script creates a `guides/` directory organized by division (PM, QA, SE, EXD).

## Guides REST API

### Deployed Service

**Production URL**: `https://mcp-server-375955300575.us-central1.run.app`

**Authentication**: Requires Google Workspace credentials

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/divisions
```

### Available Endpoints

- **GET /** - API information and endpoint list
- **GET /health** - Health check endpoint
- **GET /divisions** - List all divisions with guide counts
- **GET /divisions/{division}/guides** - List guides in a division
- **GET /guides/{path}** - Get full guide content and metadata
- **POST /search** - Semantic search using Vertex AI embeddings
  - Body: `{"query": "authentication", "top_k": 5}`
- **POST /recommendations** - Get personalized recommendations
  - Body: `{"topics": ["auth", "security"], "maturity_level": "Introduction 1", "division": "se"}`
- **POST /rebuild-index** - Rebuild Firestore vector index

### Semantic Search

Powered by Google Vertex AI and Firestore:
- **Model**: text-embedding-004 (~$0.00002 per 1,000 chars)
- **Storage**: Firestore Native with vector similarity search
- **Indexed**: 130 guides across 4 divisions
- **Search**: Natural language queries with cosine similarity scoring

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up Google Cloud credentials:

```bash
export GCP_PROJECT_ID=requirements-mcp-server
export GCP_LOCATION=us-central1
gcloud auth application-default login
```

3. Run the server:

```bash
python mcp/guides_mcp_api.py
```

Server starts on `http://localhost:8080`

### Testing

Test the deployed API:

```bash
# Test health endpoint
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/health

# Semantic search
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"query": "user authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

## Deployment

### Infrastructure

- **Platform**: Google Cloud Run (us-central1)
- **Scaling**: 0-5 instances, 2Gi memory, 1 CPU
- **Budget**: $20 USD monthly limit with alerts
- **Secrets**: Notion API credentials via Secret Manager

### CI/CD

Automated deployment via GitHub Actions:
- **Trigger**: Push to main (code changes only)
- **Build**: Docker image via Cloud Build
- **Deploy**: Automatic to Cloud Run

See `.github/workflows/deploy.yml` for configuration.

## Cost Management

- **Budget Alerts**: 50%, 75%, 90%, 100% of $20 USD
- **Cloud Run**: Scale-to-zero, max 5 instances
- **Vertex AI**: Cheapest embedding model (text-embedding-004)
- **Firestore**: Free tier enabled

## Repository Structure

```
ys-requirements-list/
├── .github/workflows/
│   ├── main.yml          # Daily Notion sync
│   └── deploy.yml        # Cloud Run deployment
├── mcp/                  # MCP server implementations
│   ├── guides_mcp_server.py  # FastMCP server (PEP 723)
│   ├── guides_mcp_api.py     # Cloud Run API
│   └── guides_mcp.py         # Alternative MCP implementation
├── scripts/              # Utility scripts
│   ├── sync_notion.py        # Notion sync script
│   └── vector_search.py      # Vertex AI + Firestore search
├── tests/                # Test files
├── guides/               # Synced from Notion
│   ├── pm/              # Product Management
│   ├── qa/              # Quality Assurance  
│   ├── se/              # Software Engineering
│   └── exd/             # Experience Design
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
└── Dockerfile           # Cloud Run container
``` 
