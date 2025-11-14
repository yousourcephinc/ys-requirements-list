# Troubleshooting Guide

Common issues and solutions for the Implementation Guides MCP server.

## Table of Contents

- [Server Issues](#server-issues)
- [Authentication Issues](#authentication-issues)
- [Search/Query Issues](#searchquery-issues)
- [MCP Integration Issues](#mcp-integration-issues)
- [Deployment Issues](#deployment-issues)
- [Performance Issues](#performance-issues)

## Server Issues

### Server Won't Start

**Symptom**: `python mcp/guides_mcp_http_server.py` fails to start

**Common Causes**:

1. **Port already in use**:
```bash
# Check what's using port 8080
lsof -ti:8080

# Kill the process
lsof -ti:8080 | xargs kill -9

# Or use a different port
PORT=8081 python mcp/guides_mcp_http_server.py
```

2. **Missing dependencies**:
```bash
# Reinstall dependencies
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt
```

3. **Python version mismatch**:
```bash
# Check Python version (requires 3.11+)
python --version

# Use specific Python version
python3.11 mcp/guides_mcp_http_server.py
```

### Server Returns 500 Errors

**Symptom**: API requests return HTTP 500 Internal Server Error

**Debug Steps**:

1. **Check server logs**:
```bash
# Look for Python tracebacks
tail -f mcp_server.log

# Or run with debug mode
DEBUG=1 python mcp/guides_mcp_http_server.py
```

2. **Verify Firestore connection**:
```python
from google.cloud import firestore
db = firestore.Client(database='implementation-guides')
print(list(db.collection('guides').limit(1).stream()))
```

3. **Check file paths**:
```python
# Test path resolution
from pathlib import Path
guides_root = Path("guides")
print(f"Guides exist: {guides_root.exists()}")
print(f"Absolute path: {guides_root.absolute()}")
```

### Guide Not Found Errors

**Symptom**: `Guide not found: se/some-guide/index.md`

**Solutions**:

1. **Verify guide exists**:
```bash
# Check if file exists
ls -la guides/se/some-guide/index.md

# List all guides
find guides -name "index.md"
```

2. **Check working directory**:
```bash
# Server should run from project root or mcp/
pwd

# Fix: run from correct directory
cd /path/to/ys-requirements-list
python mcp/guides_mcp_http_server.py
```

3. **Verify path format**:
- Paths should use `/` not `\`
- Path should be relative to `guides/` directory
- Example: `se/authentication-module---introduction-1/index.md`

## Authentication Issues

### "Unauthorized" or 401 Errors

**Symptom**: API returns 401 Unauthorized

**Solutions**:

1. **Get valid token**:
```bash
# Authenticate with gcloud
gcloud auth login
gcloud auth application-default login

# Get fresh token
TOKEN=$(gcloud auth print-identity-token)
echo $TOKEN
```

2. **Check token expiration**:
```bash
# Tokens expire after 1 hour
# Get new token
TOKEN=$(gcloud auth print-identity-token)
```

3. **Verify authorization header**:
```bash
# Correct format
curl -H "Authorization: Bearer $TOKEN" <endpoint>

# NOT: "Bearer: $TOKEN" or "Token $TOKEN"
```

### "Invalid Token" Errors

**Symptom**: Authentication fails with invalid token message

**Solutions**:

1. **Re-authenticate**:
```bash
gcloud auth revoke
gcloud auth login
gcloud auth application-default login
```

2. **Check project**:
```bash
# Verify correct project
gcloud config get-value project

# Set correct project
gcloud config set project implementation-guides-439017
```

3. **Use API key for testing**:
```bash
# Set environment variable
export IMPLEMENTATION_GUIDES_API_KEY=test-key

# Use in requests (local only)
curl -H "X-API-Key: test-key" http://localhost:8080/search
```

### Permission Denied Errors

**Symptom**: 403 Forbidden or permission denied

**Solutions**:

1. **Check domain**:
```bash
# Verify your email domain
gcloud auth list

# Production requires @you-source.com domain
```

2. **Verify IAM permissions**:
```bash
# Check your permissions
gcloud projects get-iam-policy implementation-guides-439017 \
  --filter="bindings.members:user:YOUR_EMAIL"
```

## Search/Query Issues

### No Search Results

**Symptom**: Search returns empty results

**Solutions**:

1. **Check if index exists**:
```bash
# Verify Firestore collection
gcloud firestore databases list --project=implementation-guides-439017

# Check document count
python -c "
from google.cloud import firestore
db = firestore.Client(database='implementation-guides')
docs = list(db.collection('guides').stream())
print(f'Found {len(docs)} documents')
"
```

2. **Try broader query**:
```bash
# Instead of specific terms
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "user authentication OAuth 2.0", "top_k": 5}' \
  http://localhost:8080/search

# Try broader terms
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 10}' \
  http://localhost:8080/search
```

3. **Rebuild semantic index**:
```bash
# Regenerate embeddings (expensive!)
python scripts/generate_embeddings.py --rebuild
```

### Poor Search Relevance

**Symptom**: Search returns irrelevant guides

**Solutions**:

1. **Use more specific queries**:
```json
// Instead of
{"query": "login"}

// Use
{"query": "user login authentication email password"}
```

2. **Filter by division**:
```json
{
  "query": "authentication",
  "division": "se",
  "top_k": 5
}
```

3. **Filter by maturity**:
```json
{
  "query": "OAuth setup",
  "maturity_level": "introduction-1",
  "top_k": 5
}
```

### Slow Search Performance

**Symptom**: Search takes >5 seconds

**Solutions**:

1. **Reduce top_k**:
```json
// Instead of top_k: 50
{"query": "authentication", "top_k": 10}
```

2. **Check Firestore indexes**:
```bash
gcloud firestore indexes list --database=implementation-guides
```

3. **Monitor Vertex AI quota**:
```bash
gcloud monitoring timeseries list \
  --project=implementation-guides-439017 \
  --filter='metric.type="serviceruntime.googleapis.com/api/request_count"'
```

## MCP Integration Issues

### Claude Desktop Can't Connect

**Symptom**: Claude Desktop shows MCP server as disconnected

**Solutions**:

1. **Verify config path**:
```bash
# macOS
cat ~/.config/Claude/claude_desktop_config.json

# Windows
type %APPDATA%\Claude\claude_desktop_config.json
```

2. **Check server path**:
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

3. **Test server manually**:
```bash
# Run the exact command from config
uv run /path/to/mcp/guides_mcp_server.py

# Should start without errors
```

4. **Check Claude Desktop logs**:
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log

# Windows
type %LOCALAPPDATA%\Claude\logs\mcp*.log
```

### GitHub Copilot Can't Find MCP Server

**Symptom**: Copilot doesn't show implementation guides

**Solutions**:

1. **Verify VS Code settings**:
```json
// .vscode/settings.json
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

2. **Ensure local server running**:
```bash
# Terminal 1: Start server
cd /path/to/ys-requirements-list/mcp
python guides_mcp_http_server.py

# Terminal 2: Test connection
curl http://localhost:8080/
```

3. **Reload VS Code**:
```
Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows)
> Developer: Reload Window
```

4. **Check Copilot logs**:
```
Cmd+Shift+P > Developer: Open Logs Folder
Look for GitHub Copilot logs
```

### MCP Tools Not Appearing

**Symptom**: MCP tools don't show up in AI assistant

**Solutions**:

1. **Verify server is running**:
```bash
# Check server process
ps aux | grep guides_mcp

# Check server responds
curl http://localhost:8080/
```

2. **Test MCP endpoint directly**:
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

3. **Restart AI assistant**:
- Claude Desktop: Quit and reopen
- VS Code: Reload window
- Other: Restart the application

## Deployment Issues

### Cloud Run Deployment Fails

**Symptom**: GitHub Actions deployment fails

**Solutions**:

1. **Check workflow logs**:
```bash
# View GitHub Actions logs
gh run list --workflow=deploy.yml
gh run view <run-id> --log
```

2. **Verify secrets**:
```bash
# Check GitHub secrets are set
gh secret list

# Required secrets:
# - GCP_PROJECT_ID
# - GCP_SA_KEY
```

3. **Test Docker build locally**:
```bash
# Build Docker image
docker build -t test-mcp-server .

# Run locally
docker run -p 8080:8080 test-mcp-server
```

### Cloud Run Service Unhealthy

**Symptom**: Service shows as unhealthy in Cloud Run console

**Solutions**:

1. **Check Cloud Run logs**:
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --project implementation-guides-439017
```

2. **Verify health endpoint**:
```bash
# Should return 200 OK
curl https://mcp-server-375955300575.us-central1.run.app/
```

3. **Check environment variables**:
```bash
# View Cloud Run service config
gcloud run services describe mcp-server \
  --region us-central1 \
  --project implementation-guides-439017
```

### Firestore Connection Fails in Cloud Run

**Symptom**: Cloud Run can't connect to Firestore

**Solutions**:

1. **Verify service account permissions**:
```bash
# Check service account
gcloud run services describe mcp-server \
  --region us-central1 \
  --format="value(spec.template.spec.serviceAccountName)"

# Grant Firestore permissions
gcloud projects add-iam-policy-binding implementation-guides-439017 \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/datastore.user"
```

2. **Check Firestore database name**:
```bash
# Environment variable must match database name
FIRESTORE_DATABASE=implementation-guides
```

## Performance Issues

### High Latency

**Symptom**: Requests take >3 seconds

**Solutions**:

1. **Check Cloud Run instances**:
```bash
# Increase min instances to reduce cold starts
gcloud run services update mcp-server \
  --min-instances 1 \
  --region us-central1
```

2. **Add caching**:
```python
# Cache search results (add to server code)
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, top_k: int):
    return do_search_guides(query, top_k)
```

3. **Optimize queries**:
- Reduce `top_k` value
- Use division filters
- Cache frequently accessed guides

### High Cost

**Symptom**: GCP bill higher than expected

**Solutions**:

1. **Check quota usage**:
```bash
# View Vertex AI usage
gcloud monitoring timeseries list \
  --filter='metric.type="serviceruntime.googleapis.com/quota/exceeded"'
```

2. **Optimize embeddings**:
```bash
# Don't rebuild unnecessarily
# Embeddings are cached in Firestore

# Check Firestore size
gcloud firestore databases describe implementation-guides
```

3. **Reduce Cloud Run instances**:
```bash
# Set max instances
gcloud run services update mcp-server \
  --max-instances 3 \
  --region us-central1
```

### Memory Issues

**Symptom**: Server runs out of memory

**Solutions**:

1. **Increase Cloud Run memory**:
```bash
gcloud run services update mcp-server \
  --memory 1Gi \
  --region us-central1
```

2. **Optimize guide loading**:
```python
# Don't load all guides in memory
# Load on-demand from Firestore
```

## Health Checks

### Quick Health Check

```bash
# Local server
curl http://localhost:8080/

# Production server
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/
```

### Comprehensive Health Check

```bash
# 1. Check server is running
curl http://localhost:8080/

# 2. Check divisions endpoint
curl http://localhost:8080/divisions

# 3. Check search
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}' \
  http://localhost:8080/search

# 4. Check guide retrieval
curl http://localhost:8080/guides/se/authentication-module---introduction-1/index.md

# All should return 200 OK
```

### Debug Mode

Enable verbose logging:

```bash
# Set debug environment variable
export DEBUG=1

# Run server
python mcp/guides_mcp_http_server.py
```

Or add to code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

If you can't resolve the issue:

1. **Check existing issues**: [GitHub Issues](https://github.com/yousourcephinc/ys-requirements-list/issues)
2. **Gather information**:
   - Error messages
   - Server logs
   - Steps to reproduce
   - Environment details (OS, Python version, etc.)
3. **Create new issue**: Include all gathered information

## Related Documentation

- [Local Development Guide](local-development.md)
- [API Reference](api-reference.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Configuration Reference](configuration.md)

---

**Last Updated**: November 13, 2025
