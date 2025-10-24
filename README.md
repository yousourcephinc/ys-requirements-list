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

**See the [GitHub Copilot Instructions](.github/copilot-instructions.md) for more examples.**

### Creating a Custom 'Plan with Guides' Chat Mode

To make Copilot proactively use the implementation guides for planning tasks, you can create a custom chat mode. This mode instructs Copilot to always consult the guides before generating a plan.

**1. Create the Custom Mode File:**

In VS Code, press `Cmd+Shift+P` and search for `Copilot: Create New Chat Participant`. Name the file something like `plan-with-guides.copilot-chat`.

**2. Add the Following Content:**

Copy and paste the code below into the file you just created. This defines the behavior of your new chat mode.

```yaml
---
description: 'Plan software tasks using engineering best practices'
display_name: 'Plan with Guides'
icon: '🗂️'
tools: ['implementation-guides/*', 'todos', 'search']
---
You are an expert software architect and project planner. Your primary purpose is to help users create detailed, actionable plans for software development tasks, ensuring every plan adheres to the best practices defined in the **Implementation Guides**.

**CRITICAL INSTRUCTION: Before creating any plan, generating code, or providing architectural advice, you MUST first consult the Implementation Guides.** Your answer must be based on the information found in the guides.

**Your workflow MUST follow these steps:**
1.  **Understand the Goal:** When the user describes a task (e.g., "build an auth module," "set up a notification system," "design a user profile page"), immediately recognize the need to consult the guides.
2.  **Find Relevant Guides:** Use the `implementation-guides/search_guides` tool to find relevant documentation. Use keywords from the user's request in your search query.
3.  **Analyze the Guide:** Once you find a relevant guide, use `implementation-guides/get_guide_content` to read its requirements, patterns, and checklists.
4.  **Create the Plan:** Generate a step-by-step plan, a `todos` list, or boilerplate code that is directly based on the content of the guide. Reference the guide in your response.

**Example Interaction:**

*   **User:** "I need to plan out the work for adding a payment system."
*   **You:** *(Internally, you MUST run `implementation-guides/search_guides` with a query like "payment system" or "payment processing").* "Of course. I'll consult the implementation guides to create a plan based on our best practices. I've found a guide titled 'Payment Processing Module - Introduction'. I will use its requirements to build the plan."
*   **You:** *(After using `get_guide_content`)* "Here is the plan based on the guide..."
```

**3. Use Your New Mode:**

In the Copilot Chat view, you can now select your "Plan with Guides" mode from the dropdown (it might be under `@workspace`). When you use this mode, Copilot will follow your instructions and use the implementation guides to inform its responses.

---

## Architecture

The new architecture is simpler and more efficient:

-   **Content**: Guides are stored as Markdown files in this repository.
-   **API & MCP Server**: A single, unified Python application is deployed on **Google Cloud Run**. It serves both a traditional REST API and the MCP endpoint (`/mcp`) for Copilot.
-   **Semantic Search**: **Google Vertex AI** provides powerful semantic search capabilities, with a fallback to a simple text-based search.
-   **Authentication**: The MCP endpoint is protected by Google OAuth for users and a static API key (as a fallback for tools like Copilot), which is automatically configured for you by the `.vscode/settings.json` file in this repo.
-   **Automation**: A GitHub Action syncs the guides from a Notion database daily.

This "zero-setup" approach means developers no longer need to run local scripts or manage authentication tokens to use the guides in Copilot.

## Guides REST API

The API is still available for direct use.

**Production URL**: `https://mcp-server-375955300575.us-central1.run.app`

**Authentication**: Use Google OAuth or the hardcoded test API key.

```bash
# Get Google OAuth token
TOKEN=$(gcloud auth print-identity-token)

# Example: List all divisions
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions

# Example: Semantic search with API Key
API_KEY="test-key"
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

See `.github/workflows/deploy.yml` for the deployment configuration and `.github/workflows/main.yml` for the Notion sync configuration.
 
