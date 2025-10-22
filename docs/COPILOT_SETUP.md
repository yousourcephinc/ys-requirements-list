# GitHub Copilot Setup Guide

This guide explains how to use the Implementation Guides directly within VS Code via GitHub Copilot.

## How It Works

The system is now a "zero-setup" configuration. The MCP (Model Context Protocol) server is hosted remotely on Google Cloud Run. This repository contains a `.vscode/settings.json` file that tells your local VS Code and Copilot how to connect to it securely.

There is **no local server or script to run**.

## Prerequisites

1.  **Visual Studio Code** with the latest **GitHub Copilot** extension installed.
2.  You must be a member of the `yousourcephinc` GitHub organization to access this repository.

## Installation

The installation is automatic when you open this project in VS Code.

1.  **Clone or open the `ys-requirements-list` repository in VS Code.**
2.  A dialog may appear asking if you "trust the authors of the files in this folder". **You must select "Yes, I trust the authors"**. This allows VS Code to read the `.vscode/settings.json` file.
3.  **Reload the VS Code window** to ensure Copilot loads the new tool.
    *   Open the Command Palette (`View > Command Palette` or `Cmd+Shift+P`).
    *   Type `Developer: Reload Window` and press Enter.

## Verification

To verify that the `implementation-guides` tool is active:

1.  Open the Copilot Chat view in VS Code.
2.  Type `@workspace /help`.
3.  You should see `implementation-guides` listed as an available tool.

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

The new, simplified architecture:

```
GitHub Copilot Chat (in VS Code)
    │
    └─> HTTPS Request (with API Key)
        │
        ▼
Google Cloud Run Endpoint (`/mcp`)
    │
    ├─> Reads guide files from its own filesystem
    └─> Queries Vertex AI + Firestore for semantic search
```

Authentication is handled by a simple API key, which is pre-configured for you in the workspace settings. You no longer need to authenticate with `gcloud` for Copilot to work.

## Troubleshooting

*   **Tool not showing up:** The most common issue is not "trusting" the workspace. Make sure you've trusted it and reloaded the window.
*   **Authentication Errors:** The API key is hardcoded to `test-key`. If you see auth errors, it might mean the deployed server has a different key. The `.vscode/settings.json` file would need to be updated.
*   **Slow First Request:** The Cloud Run service can "scale to zero," meaning it might be asleep. The very first request you make in a while might take a few seconds to "wake up" the server. Subsequent requests will be fast.
