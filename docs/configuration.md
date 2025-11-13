# Configuration Reference

Complete reference for environment variables and configuration options.

## Environment Variables

### Required Variables

| Variable | Description | Example | Used By |
|----------|-------------|---------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | `implementation-guides-439017` | All GCP services |
| `FIRESTORE_DATABASE` | Firestore database name | `implementation-guides` | Semantic search, MCP server |

### Optional Variables

| Variable | Description | Default | Used By |
|----------|-------------|---------|---------|
| `NOTION_API_KEY` | Notion integration API key | - | `sync_notion.py`, `upload_foundational_to_notion.py` |
| `NOTION_DATABASE_ID` | Notion database ID | Auto-detected | `sync_notion.py` |
| `IMPLEMENTATION_GUIDES_API_KEY` | Static API key for tools | `test-key` | MCP server (local only) |
| `PORT` | Server port | `8080` | HTTP server |
| `DEBUG` | Enable debug logging | `false` | All scripts |
| `VERTEX_AI_LOCATION` | Vertex AI region | `us-central1` | `generate_embeddings.py` |

### Cloud Run Variables

| Variable | Description | Default | Set By |
|----------|-------------|---------|--------|
| `K_SERVICE` | Cloud Run service name | - | Cloud Run |
| `K_REVISION` | Cloud Run revision | - | Cloud Run |
| `K_CONFIGURATION` | Cloud Run configuration | - | Cloud Run |

## Configuration Files

### .env

Local development environment variables.

**Location**: Repository root

**Example**:
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=implementation-guides-439017
FIRESTORE_DATABASE=implementation-guides
VERTEX_AI_LOCATION=us-central1

# Notion (optional)
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxx

# Local development
IMPLEMENTATION_GUIDES_API_KEY=test-key
DEBUG=true
PORT=8080
```

**Load**:
```bash
# Manual
source .env

# With direnv
echo "dotenv" > .envrc
direnv allow

# Python (python-dotenv)
from dotenv import load_dotenv
load_dotenv()
```

### .vscode/settings.json

VS Code configuration for GitHub Copilot MCP integration.

**Location**: Project root (created by `specify init`)

**Example**:
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

### claude_desktop_config.json

Claude Desktop MCP server configuration.

**Location**:
- macOS: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Example**:
```json
{
  "mcpServers": {
    "implementation-guides": {
      "command": "uv",
      "args": [
        "run",
        "/absolute/path/to/ys-requirements-list/mcp/guides_mcp_server.py"
      ]
    }
  }
}
```

**Install**:
```bash
uv run mcp install mcp/guides_mcp_server.py \
  --name "Implementation Guides"
```

### pyproject.toml

Python project configuration.

**Location**: Repository root

**Key Sections**:
```toml
[project]
name = "implementation-guides"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0.0",
    "notion-client>=2.0.0",
    "google-cloud-firestore>=2.11.0",
    "google-cloud-aiplatform>=1.38.0",
    # ... more dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]
```

### requirements.txt

Pip-compatible dependencies list.

**Location**: Repository root

**Generate from pyproject.toml**:
```bash
uv pip compile pyproject.toml -o requirements.txt
```

## Google Cloud Configuration

### Project Setup

```bash
# Set default project
gcloud config set project implementation-guides-439017

# Enable required APIs
gcloud services enable \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com

# Set default region
gcloud config set run/region us-central1
```

### Firestore Configuration

**Database**: `implementation-guides`

**Collections**:
- `guides` - Vector embeddings and metadata

**Indexes**:
```bash
# List indexes
gcloud firestore indexes list --database=implementation-guides

# Create composite index (if needed)
gcloud firestore indexes composite create \
  --collection-group=guides \
  --field-config field-path=division,order=ASCENDING \
  --field-config field-path=maturity,order=ASCENDING \
  --database=implementation-guides
```

**Security Rules**:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /guides/{guide} {
      // Allow read for authenticated users
      allow read: if request.auth != null;
      
      // Allow write for service account only
      allow write: if request.auth.token.email.matches('.*@implementation-guides-.*');
    }
  }
}
```

### Vertex AI Configuration

**Model**: `textembedding-gecko@003`
**Region**: `us-central1`
**Dimensions**: 768

**Quota**:
- Requests per minute: 300
- Requests per day: 1,000,000

**Check quota**:
```bash
gcloud compute project-info describe \
  --project=implementation-guides-439017 \
  --format="yaml(quotas)"
```

### Cloud Run Configuration

**Service**: `mcp-server`
**Region**: `us-central1`
**Image**: Auto-built from Dockerfile

**Current Settings**:
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: mcp-server
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: '5'
        autoscaling.knative.dev/minScale: '0'
    spec:
      containers:
      - image: gcr.io/implementation-guides-439017/mcp-server:latest
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: implementation-guides-439017
        - name: FIRESTORE_DATABASE
          value: implementation-guides
        resources:
          limits:
            cpu: '1'
            memory: 512Mi
        ports:
        - containerPort: 8080
```

**Update settings**:
```bash
# Set memory
gcloud run services update mcp-server \
  --memory 1Gi \
  --region us-central1

# Set CPU
gcloud run services update mcp-server \
  --cpu 2 \
  --region us-central1

# Set concurrency
gcloud run services update mcp-server \
  --concurrency 80 \
  --region us-central1

# Set min/max instances
gcloud run services update mcp-server \
  --min-instances 1 \
  --max-instances 10 \
  --region us-central1
```

### Secret Manager

Secrets stored in Google Secret Manager:

| Secret Name | Description | Used By |
|-------------|-------------|---------|
| `notion-api-key` | Notion integration API key | GitHub Actions sync |
| `implementation-guides-api-key` | Static API key | MCP tools (optional) |

**Access secrets**:
```bash
# View secret
gcloud secrets versions access latest \
  --secret=notion-api-key \
  --project=implementation-guides-439017

# Add secret version
echo -n "new-secret-value" | gcloud secrets versions add notion-api-key \
  --data-file=- \
  --project=implementation-guides-439017
```

## GitHub Configuration

### Repository Secrets

**Location**: Settings → Secrets and variables → Actions

**Required Secrets**:

| Secret | Description | Used By |
|--------|-------------|---------|
| `GCP_PROJECT_ID` | GCP project ID | All workflows |
| `GCP_SA_KEY` | Service account JSON key | Deployment |
| `NOTION_API_KEY` | Notion API integration key | Notion sync |

**Set secrets**:
```bash
gh secret set GCP_PROJECT_ID --body "implementation-guides-439017"
gh secret set NOTION_API_KEY --body "secret_xxxxx"

# From file
gh secret set GCP_SA_KEY < service-account-key.json
```

### GitHub Actions Configuration

**Workflows**:
- `.github/workflows/deploy.yml` - Deploy to Cloud Run
- `.github/workflows/sync-notion.yml` - Daily Notion sync
- `.github/workflows/generate-embeddings.yml` - Generate embeddings

**Example workflow configuration**:
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_NAME: mcp-server
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - id: auth
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy $SERVICE_NAME \
            --source . \
            --region $REGION \
            --project $PROJECT_ID
```

## Performance Tuning

### Server Performance

```bash
# Increase workers (gunicorn)
gunicorn --workers 4 --threads 2 mcp.guides_mcp_http_server:app

# Adjust timeout
gunicorn --timeout 120 mcp.guides_mcp_http_server:app

# Use eventlet for async
gunicorn --worker-class eventlet mcp.guides_mcp_http_server:app
```

### Caching

```python
# Add to server code
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_guide_content(path: str):
    return get_guide_content(path)

@lru_cache(maxsize=100)
def cached_search(query: str, top_k: int):
    return search_guides(query, top_k)
```

### Firestore Optimization

```bash
# Create composite indexes for common queries
gcloud firestore indexes composite create \
  --collection-group=guides \
  --field-config field-path=division,order=ASCENDING \
  --field-config field-path=score,order=DESCENDING \
  --database=implementation-guides
```

## Cost Management

### Current Costs

- **Cloud Run**: ~$5/month (with min instances = 0)
- **Firestore**: ~$5/month (< 1 GB storage)
- **Vertex AI**: ~$10/month (embeddings)
- **Total**: ~$20/month

### Cost Optimization

```bash
# Reduce min instances
gcloud run services update mcp-server \
  --min-instances 0 \
  --region us-central1

# Set budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Implementation Guides Budget" \
  --budget-amount=50 \
  --threshold-rule=percent=90

# Monitor costs
gcloud billing accounts list
gcloud billing projects link implementation-guides-439017 \
  --billing-account=BILLING_ACCOUNT_ID
```

## Security Configuration

### IAM Roles

```bash
# Grant Firestore access
gcloud projects add-iam-policy-binding implementation-guides-439017 \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

# Grant Vertex AI access
gcloud projects add-iam-policy-binding implementation-guides-439017 \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding implementation-guides-439017 \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

### Authentication

**Domain-based authentication** (production):
```python
# In Cloud Run, check user domain
@app.before_request
def check_domain():
    if request.path.startswith('/api/'):
        token = request.headers.get('Authorization')
        user_info = verify_token(token)
        if not user_info['email'].endswith('@yoursource.ph'):
            abort(403, 'Access denied')
```

## Related Documentation

- [Local Development Guide](local-development.md)
- [Deployment Guide](DEPLOYMENT.md)
- [API Reference](api-reference.md)
- [Troubleshooting](troubleshooting.md)

---

**Last Updated**: November 13, 2025
