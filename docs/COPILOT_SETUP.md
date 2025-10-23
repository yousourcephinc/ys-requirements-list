# GitHub Copilot Setup Guide

This guide explains how to use the Implementation Guides directly within VS Code via GitHub Copilot.

## How It Works

The Implementation Guides are accessible through a remote MCP (Model Context Protocol) server hosted on Google Cloud Run. You can configure GitHub Copilot to connect to this server by adding a simple configuration to your VS Code workspace settings.

There is **no local server or script to run**, and **no repository cloning required**.

## Prerequisites

1. **Visual Studio Code** with the latest **GitHub Copilot** extension installed.
2. **Google Cloud SDK authenticated** with an account from the `you-source.com` domain:
   ```bash
   gcloud auth login
   ```

## Installation

Add the following configuration to your project's `.vscode/settings.json` file (create the file if it doesn't exist):

```json
{
  "github.copilot.advanced": {
    "tools": {
      "implementation-guides": {
        "type": "http",
        "url": "https://mcp-server-375955300575.us-central1.run.app/mcp",
        "auth": {
          "type": "header",
          "header": "Authorization",
          "value": "Bearer test-key"
        }
      }
    }
  }
}
```

**Note:** For GitHub Copilot, use the `test-key` as shown above. For other AI tools that support dynamic authentication, you can use Google OAuth tokens instead:

```json
{
  "github.copilot.advanced": {
    "tools": {
      "implementation-guides": {
        "type": "http",
        "url": "https://mcp-server-375955300575.us-central1.run.app/mcp",
        "auth": {
          "type": "header",
          "header": "Authorization",
          "value": "Bearer $(gcloud auth print-identity-token)"
        }
      }
    }
  }
}
```

If your tool doesn't support the `$(...)` syntax, run `gcloud auth print-identity-token` manually and paste the token.

## Verification

To verify that the `implementation-guides` tool is active:

1. Open the Copilot Chat view in VS Code.
2. Type `@workspace /help`.
3. You should see `implementation-guides` listed as an available tool.

If you don't see it, try reloading the window again or ensure you have trusted the workspace.

## Usage in GitHub Copilot Chat

Always start your query with `@workspace` to give Copilot access to the guides.

### Example Commands

*   **List all categories:**
    `@workspace What are the available guide divisions?`

*   **List guides in a category:**
    `@workspace Show me all guides for Software Engineering (se)`

*   **Search for a specific topic:**
    `@workspace Search for guides about user authentication and SSO`

*   **Get the content of a guide:**
    `@workspace Get the content of the guide with path "se/authentication-module---introduction-1/index.md"`

### Example Workflows

#### 1. Starting a New Feature
> **You:** `@workspace I need to build a notification system. What guides are available?`
>
> **Copilot:** (Uses `search_guides`) "I found the following guides related to notifications:..."

#### 2. Implementing Code
> **You:** `@workspace Based on the 'notifications-intro-1' guide, generate the initial Python code for a notification service.`
>
> **Copilot:** (Uses `get_guide_content` to read the guide, then generates code) "Certainly. Here is a Flask-based notification service that follows the requirements outlined in the guide..."

## Architecture

The architecture supports both API key authentication (for Copilot) and Google OAuth (for other tools):

```
GitHub Copilot Chat (in VS Code)
    │
    └─> HTTPS Request (with API Key: "test-key")
        │
        ▼
Google Cloud Run Endpoint (`/mcp`)
    │
    ├─> Validates API key or Google identity token
    ├─> Reads guide files from its own filesystem
    └─> Queries Vertex AI + Firestore for semantic search

Other AI Tools
    │
    └─> HTTPS Request (with Google OAuth token)
        │
        ▼
    Same Cloud Run Endpoint
```