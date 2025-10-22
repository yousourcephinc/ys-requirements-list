# ys-requirements-list

Repository of implementation guides, accessible directly through GitHub Copilot.

## 🤖 GitHub Copilot Integration (Zero-Setup)

**Use implementation guides directly in VS Code with GitHub Copilot!**

This repository is configured to automatically connect to a hosted MCP (Model Context Protocol) server, giving you and your team instant access to all guides from within the editor.

### Quick Setup

1.  **Open this repository in VS Code.**
2.  If prompted, **trust the workspace**.
3.  **Reload the VS Code window** (`Cmd+Shift+P` → `Developer: Reload Window`).

That's it. You can now use `@workspace` in Copilot Chat.

```
@workspace Search for authentication guides
@workspace Recommend payment guides at Introduction 1 for SE
```

**See the [Copilot Usage Guide](docs/COPILOT_SETUP.md) for more examples.**

---

## Architecture

The new architecture is simpler and more efficient:

-   **Content**: Guides are stored as Markdown files in this repository.
-   **API & MCP Server**: A single, unified Python application is deployed on **Google Cloud Run**. It serves both a traditional REST API and the MCP endpoint (`/mcp`) for Copilot.
-   **Semantic Search**: **Google Vertex AI** and **Firestore** provide powerful semantic search capabilities.
-   **Authentication**: The MCP endpoint is protected by a simple API key, which is automatically configured for you by the `.vscode/settings.json` file in this repo.
-   **Automation**: A GitHub Action syncs the guides from a Notion database daily.

This "zero-setup" approach means developers no longer need to run local scripts or manage authentication tokens to use the guides in Copilot.

## Guides REST API

The API is still available for direct use.

**Production URL**: `https://mcp-server-375955300575.us-central1.run.app`

**Authentication**: Use the hardcoded test API key for now.

```bash
API_KEY="test-key"

# Example: List all divisions
curl -H "Authorization: Bearer $API_KEY" \
  https://mcp-server-375955300575.us-central1.run.app/divisions

# Example: Semantic search
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "user authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

### Local Development

1.  Install dependencies: `pip install -r requirements.txt`
2.  Run the server: `python mcp/guides_mcp_http_server.py`
3.  The server will start on `http://localhost:8080`.

## Deployment

Deployment is handled automatically via GitHub Actions when changes are pushed to the `main` branch. The action builds a Docker container and deploys it to Google Cloud Run.

See `.github/workflows/main.yml` for configuration.
 
