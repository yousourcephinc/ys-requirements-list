# GitHub Copilot MCP Setup

Configure the Implementation Guides MCP server for GitHub Copilot in VS Code.

## Prerequisites

1. **VS Code** with GitHub Copilot extension installed
2. **GitHub Copilot subscription** (Individual, Business, or Enterprise)
3. **uv package manager:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. **Google Cloud SDK authenticated:**
   ```bash
   gcloud auth login
   ```

## Installation

### Option 1: Workspace Settings (Recommended for Teams)

1. Create or edit `.vscode/settings.json` in your project:
   ```json
   {
     "github.copilot.chat.mcp.servers": {
       "implementation-guides": {
         "command": "uv",
         "args": [
           "--quiet",
           "run",
           "--with",
           "mcp>=1.2.0",
           "--with",
           "httpx>=0.27.0",
           "https://raw.githubusercontent.com/yousourcephinc/ys-requirements-list/main/mcp/guides_mcp_server.py"
         ],
         "env": {
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

2. Reload VS Code window (Cmd+Shift+P → "Developer: Reload Window")

### Option 2: User Settings (Global for All Projects)

1. Open VS Code Settings (Cmd+, or Ctrl+,)
2. Search for "copilot mcp"
3. Click "Edit in settings.json"
4. Add the same configuration as above

## Usage in GitHub Copilot Chat

Once configured, you can use these commands in Copilot Chat:

### Ask About Guides
```
@workspace What implementation guides are available?
```

### Search for Specific Topics
```
@workspace Search guides for user authentication and OAuth
```

### Get Recommendations
```
@workspace Recommend payment processing guides at Introduction 1 level for software engineers
```

### Implement with Guide Context
```
@workspace Implement user authentication following the SE Introduction 1 guide
```

### Browse by Division
```
@workspace Show me all Quality Assurance guides
```

## Available Tools

GitHub Copilot can use these MCP tools:

1. **list_guide_divisions** - List all divisions (PM, QA, SE, EXD)
2. **list_guides_by_division** - List guides in a specific division
3. **get_guide_content** - Get full guide content and requirements
4. **search_guides** - Semantic search with AI embeddings
5. **get_guide_recommendations** - Personalized recommendations

## Verification

To verify the MCP server is working:

1. Open Copilot Chat in VS Code
2. Type: `@workspace /help`
3. You should see "implementation-guides" listed under available tools

## Example Workflows

### 1. Implementing Authentication
```
You: @workspace I need to implement user authentication for a new project

Copilot: [Uses search_guides to find auth guides]
Let me search for authentication implementation guides...

[Shows relevant guides with requirements]

Based on the Authentication Module - Introduction 1 guide for SE:
- Functional requirements include...
- Security requirements include...
- Here's a code implementation...
```

### 2. Code Review with Guide Standards
```
You: @workspace Review this payment processing code against our guides

Copilot: [Uses search_guides + get_guide_content]
Let me check this against the Payment Processing guides...

[Compares code with guide requirements]

Your code is missing:
1. PCI DSS compliance checks (required by Payment Processing - Introduction 1)
2. Idempotency keys for transaction safety
...
```

### 3. Project Planning
```
You: @workspace What guides should I follow for a user management system at Introduction 1 level?

Copilot: [Uses get_guide_recommendations]
For a user management system at Introduction 1, you should follow:

1. User Management Module - Introduction 1 (SE)
2. Authentication Module - Introduction 1 (SE)
3. Settings & Preferences - Introduction 1 (EXD)
...
```

## Troubleshooting

### MCP Server Not Found

Check VS Code Output panel:
1. View → Output
2. Select "GitHub Copilot Chat" from dropdown
3. Look for MCP server connection errors

### Authentication Errors

Verify gcloud authentication:
```bash
gcloud auth login
gcloud auth print-identity-token
```

### Server Not Loading

1. Check that `uv` is in PATH: `which uv`
2. Try running server manually:
   ```bash
   uv run --with mcp --with httpx https://raw.githubusercontent.com/yousourcephinc/ys-requirements-list/main/mcp/guides_mcp_server.py
   ```
3. Check for Python errors in terminal

### Slow Responses

- First request may be slow (Cloud Run cold start)
- Subsequent requests should be fast
- Consider keeping a browser tab open to the API to keep it warm

## Best Practices

### 1. Use @workspace Mention
Always mention `@workspace` to give Copilot access to MCP tools:
```
✅ @workspace Search for authentication guides
❌ Search for authentication guides (Copilot won't use MCP tools)
```

### 2. Be Specific About Division/Level
```
✅ @workspace Recommend SE guides at Introduction 1 for authentication
❌ @workspace Find auth stuff
```

### 3. Reference Guides in Code Comments
```python
# Following User Management Module - Introduction 1 (SE)
class UserManager:
    """Implements user CRUD operations per guide requirements"""
```

## Team Setup

For team-wide adoption:

1. **Add to repository's `.vscode/settings.json`**
   - Commit to version control
   - All team members get MCP automatically

2. **Add to README.md**
   ```markdown
   ## AI-Assisted Development
   
   This project uses implementation guides via MCP.
   GitHub Copilot users: The guides are automatically available.
   Just use @workspace in Copilot Chat!
   ```

3. **Onboarding Checklist**
   - [ ] VS Code with Copilot installed
   - [ ] uv package manager installed
   - [ ] gcloud auth configured
   - [ ] Workspace settings loaded

## Architecture

```
GitHub Copilot Chat (VS Code)
    ↓ MCP Protocol (stdio)
Local MCP Server (Python)
    ↓ HTTPS + OAuth
Cloud Run REST API
    ↓
Vertex AI + Firestore
```

The MCP server runs locally and authenticates using your gcloud credentials.

## Links

- [GitHub Copilot MCP Docs](https://docs.github.com/en/copilot/using-github-copilot/using-mcp-with-github-copilot)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Cloud Run Endpoint](https://mcp-server-375955300575.us-central1.run.app)
