# Implementation Guides MCP Server Setup

Get AI coding assistants (Claude, VS Code Copilot, etc.) connected to your company's implementation guides in under 5 minutes.

## What You'll Get

Once set up, you can ask your AI assistant:
- **"Search for authentication guides"** → Finds relevant SE guides with code patterns
- **"Show me payment module requirements"** → Returns functional & security requirements
- **"What divisions exist?"** → Lists PM, QA, SE, EXD with guide counts
- **"Recommend guides for user management"** → Suggests relevant guides by maturity level

## Quick Start (3 Steps)

### Step 1: Install Prerequisites

**Install uv package manager:**

**macOS/Linux:**
```bash
# Copy and paste this entire block:
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # or: source ~/.bashrc

# Verify installation:
uv --version  # Should show: uv 0.x.x
```

**Windows:**
```powershell
# Run in PowerShell as Administrator:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart PowerShell, then verify:
uv --version  # Should show: uv 0.x.x
```

**Install Google Cloud CLI:**

**macOS:**
```bash
# With Homebrew (recommended):
brew install google-cloud-sdk

# Without Homebrew:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL  # Restart shell

# Verify:
gcloud --version  # Should show: Google Cloud SDK xxx.x.x
```

**Windows:**
```powershell
# Download and run the installer:
# https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe

# Or use PowerShell to download:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:TEMP\GoogleCloudSDKInstaller.exe")
Start-Process "$env:TEMP\GoogleCloudSDKInstaller.exe"

# After installation, restart PowerShell and verify:
gcloud --version  # Should show: Google Cloud SDK xxx.x.x
```

**Linux:**
```bash
# Copy and paste this entire block:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL  # Restart shell

# Verify:
gcloud --version  # Should show: Google Cloud SDK xxx.x.x
```

### Step 2: Authenticate with Google

**macOS/Linux:**
```bash
# Login with your @you-source.com account:
gcloud auth login

# Follow the browser prompts to authorize

# Verify authentication:
gcloud auth print-identity-token
# Should output a long JWT token starting with "eyJ..."
```

**Windows PowerShell:**
```powershell
# Login with your @you-source.com account:
gcloud auth login

# Follow the browser prompts to authorize

# Verify authentication:
gcloud auth print-identity-token
# Should output a long JWT token starting with "eyJ..."
```

### Step 3: Connect to Claude Desktop

**One command installation:**

**macOS/Linux:**
```bash
# Navigate to the repository (update this path):
cd ~/code/ys-requirements-list

# Install MCP server to Claude:
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"
```

**Windows PowerShell:**
```powershell
# Navigate to the repository (update this path):
cd $env:USERPROFILE\code\ys-requirements-list

# Install MCP server to Claude:
uv run mcp install mcp/guides_mcp_server.py --name "Implementation Guides"
```

**Expected output:**
```
✓ Installed Implementation Guides to Claude Desktop
✓ Configuration written to claude_desktop_config.json
✓ Restart Claude Desktop to activate
```

**Restart Claude Desktop:**
- macOS: Quit (`Cmd+Q`) and reopen
- Windows: Close completely and reopen

## Verify It's Working

Open Claude Desktop and ask:

```
What guide divisions are available?
```

**Expected response:**
Claude should show 🔧 (tools icon) and return:
```
I found 4 divisions:
- PM (Product Management): 25 guides
- QA (Quality Assurance): 30 guides  
- SE (Software Engineering): 70 guides
- EXD (Experience Design): 15 guides
```

## Common Issues & Fixes

### ❌ "Command not found: uv"

**Problem:** Shell hasn't reloaded after uv installation.

**Fix (macOS/Linux):**
```bash
# Reload your shell:
source ~/.zshrc  # or: source ~/.bashrc

# Or restart your terminal completely
```

**Fix (Windows):**
```powershell
# Restart PowerShell completely
# Or refresh environment variables:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify:
uv --version
```

### ❌ "Command not found: gcloud"

**Problem:** Google Cloud SDK not in PATH.

**Fix (macOS):**
```bash
# Add to PATH manually:
echo 'export PATH=$HOME/google-cloud-sdk/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# Or run the installer's init script:
~/google-cloud-sdk/install.sh
```

**Fix (Windows):**
```powershell
# Check if gcloud exists:
Test-Path "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

# If True, add to PATH:
[Environment]::SetEnvironmentVariable(
    "Path",
    "$env:Path;$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin",
    "User"
)

# Restart PowerShell and verify:
gcloud --version
```

### ❌ "Authentication failed" or "Invalid credentials"

**Problem:** Not logged into gcloud or wrong Google account.

**Fix:**
```bash
# Check current account:
gcloud auth list

# Login again with correct @you-source.com account:
gcloud auth login

# Test authentication:
gcloud auth print-identity-token
```

### ❌ Tools not showing in Claude Desktop

**Problem:** Claude didn't reload or config wasn't written.

**Fix (macOS):**
```bash
# 1. Verify config was created:
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Should contain "implementation-guides" entry

# 2. Completely quit Claude (Cmd+Q)
# 3. Reopen Claude Desktop
# 4. Look for 🔧 icon when you ask a question
```

**Fix (Windows):**
```powershell
# 1. Verify config was created:
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"

# Should contain "implementation-guides" entry

# 2. Completely close Claude (Alt+F4)
# 3. Reopen Claude Desktop
# 4. Look for 🔧 icon when you ask a question
```

### ❌ "Connection timeout" or "Server not responding"

**Problem:** Cloud Run service is cold-starting.

**Fix:**
- **Wait 10-15 seconds** and try again
- Cloud Run scales from 0 → 1 instance on first request
- Subsequent requests are fast (<200ms)

### ❌ Windows: "uv.exe is not recognized"

**Problem:** uv not installed correctly or not in PATH.

**Fix:**
```powershell
# Reinstall uv:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Manually add to PATH:
$uvPath = "$env:USERPROFILE\.cargo\bin"
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$uvPath", "User")

# Restart PowerShell:
exit
# Open new PowerShell window
uv --version
```

### ❌ Windows: "Access Denied" when running PowerShell commands

**Problem:** PowerShell execution policy blocks scripts.

**Fix:**
```powershell
# Run PowerShell as Administrator
# Set execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Retry the installation
```

## Using with VS Code Copilot

VS Code uses a different configuration file. Here's the complete setup:

**macOS/Linux:**

```bash
# Create directory if it doesn't exist:
mkdir -p ~/.vscode

# Create/edit settings file:
code ~/.vscode/settings.json
```

**Windows PowerShell:**

```powershell
# Create directory if it doesn't exist:
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.vscode"

# Create/edit settings file:
code "$env:USERPROFILE\.vscode\settings.json"
```

**Add this configuration (all platforms):**

```json
{
  "github.copilot.advanced": {
    "mcp": {
      "servers": {
        "implementation-guides": {
          "command": "uv",
          "args": [
            "run",
            "/absolute/path/to/ys-requirements-list/mcp/guides_mcp_server.py"
          ]
        }
      }
    }
  }
}
```

**Update the path:**

**macOS/Linux:**
- Replace `/absolute/path/to/` with your actual path
- Find it with: `pwd` when you're in the ys-requirements-list directory
- Example: `/Users/yourname/code/ys-requirements-list/mcp/guides_mcp_server.py`

**Windows:**
- Use Windows path format with forward slashes or escaped backslashes
- Find it with: `pwd` in PowerShell when you're in the ys-requirements-list directory
- Example: `C:/Users/yourname/code/ys-requirements-list/mcp/guides_mcp_server.py`
- Or: `C:\\Users\\yourname\\code\\ys-requirements-list\\mcp\\guides_mcp_server.py`

**Reload VS Code:**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type "Developer: Reload Window"
- Press Enter

**Verify in Copilot Chat:**

Ask Copilot:
```
@workspace List available guide divisions
```

Copilot should use the MCP server to fetch divisions.

## Manual Configuration (Alternative Method)

If the `uv run mcp install` command doesn't work, configure manually:

**1. Find your Claude config file:**

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
# Look for: claude_desktop_config.json
```

**Windows PowerShell:**
```powershell
explorer "$env:APPDATA\Claude"
# Look for: claude_desktop_config.json
```

**2. Edit `claude_desktop_config.json`:**

If the file doesn't exist, create it with this content:

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

**3. Update the path:**

**macOS/Linux:**
```bash
# Find your path:
cd ~/code/ys-requirements-list
pwd
# Output example: /Users/yourname/code/ys-requirements-list

# Use this output in the config file:
# "/Users/yourname/code/ys-requirements-list/mcp/guides_mcp_server.py"
```

**Windows PowerShell:**
```powershell
# Find your path:
cd $env:USERPROFILE\code\ys-requirements-list
(Get-Location).Path
# Output example: C:\Users\yourname\code\ys-requirements-list

# Use this output in the config file with forward slashes:
# "C:/Users/yourname/code/ys-requirements-list/mcp/guides_mcp_server.py"
# Or with escaped backslashes:
# "C:\\Users\\yourname\\code\\ys-requirements-list\\mcp\\guides_mcp_server.py"
```

**4. Restart Claude Desktop**

## Available Tools Reference

You don't need to memorize these - just ask naturally and Claude will pick the right tool:

| Tool | What It Does | Example Question |
|------|--------------|------------------|
| `list_guide_divisions` | Shows all divisions (PM/QA/SE/EXD) | "What divisions exist?" |
| `list_guides_by_division` | Lists guides in one division | "Show me all SE guides" |
| `get_guide_content` | Fetches a specific guide | "Get the authentication guide" |
| `search_guides` | Semantic search with AI | "Find OAuth guides" |
| `get_guide_recommendations` | Suggests relevant guides | "Recommend payment guides" |

## Testing the Server Directly

Want to test without Claude? Use the built-in MCP Inspector:

**macOS/Linux:**
```bash
cd ~/code/ys-requirements-list
uv run mcp dev mcp/guides_mcp_server.py
```

**Windows PowerShell:**
```powershell
cd $env:USERPROFILE\code\ys-requirements-list
uv run mcp dev mcp/guides_mcp_server.py
```

This opens a web UI at `http://localhost:5173` where you can:
- ✅ Test each tool with sample inputs
- ✅ See request/response payloads
- ✅ Debug authentication issues
- ✅ Verify server is working

## How It Works (Optional Reading)

```
┌─────────────────────┐
│  You ask Claude:    │  "Search for auth guides"
│  "Find auth guides" │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Claude Desktop    │  Selects search_guides tool
└──────────┬──────────┘
           │ MCP Protocol (local)
           ▼
┌─────────────────────┐
│  MCP Server (local) │  Runs on your machine
│  guides_mcp_server  │  Gets gcloud token
└──────────┬──────────┘
           │ HTTPS + Google OAuth
           ▼
┌─────────────────────┐
│   Cloud Run API     │  Production service
│   (Google Cloud)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Vertex AI Embeddings│  Semantic search
│ + Firestore DB      │  Returns top matches
└─────────────────────┘
```

**Key points:**
- MCP server runs **locally** on your machine
- Uses **your gcloud credentials** (no API keys needed)
- Calls **production API** in Google Cloud
- **Real-time search** across 130+ implementation guides
- **Automatic authentication** via Google Workspace

## Security & Privacy

✅ **Your credentials stay local** - Never sent to the API  
✅ **Token-based authentication** - Temporary tokens (expire in 1 hour)  
✅ **Domain-restricted** - Only `@you-source.com` accounts  
✅ **Runs on your machine** - No external MCP server  
✅ **Audit trail** - All API calls logged in Cloud Run  

## Getting Help

**Check logs if something goes wrong:**

**macOS:**
```bash
# Claude Desktop logs:
tail -f ~/Library/Logs/Claude/mcp*.log

# Look for:
# - Authentication errors → gcloud auth login
# - Connection errors → Check internet connection
# - Tool errors → Run uv run mcp dev to debug
```

**Windows PowerShell:**
```powershell
# Claude Desktop logs:
Get-Content "$env:APPDATA\Claude\logs\mcp-*.log" -Tail 50

# Or continuously monitor:
Get-Content "$env:APPDATA\Claude\logs\mcp-*.log" -Wait -Tail 50

# Look for:
# - Authentication errors → gcloud auth login
# - Connection errors → Check internet connection
# - Tool errors → Run uv run mcp dev to debug
```

**Still stuck?**

1. Run the MCP Inspector: `uv run mcp dev mcp/guides_mcp_server.py`
2. Test authentication: `gcloud auth print-identity-token`
3. Check Claude config:
   - macOS: `cat ~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - Windows: `Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"`
4. Verify uv works: `uv --version`

## Next Steps

Once you're connected:

1. **Try natural questions:**
   - "Search for guides about user authentication and security"
   - "What PM guides are at Introduction 1 level?"
   - "Show me the payment module requirements"

2. **Use in your workflow:**
   - Ask before implementing new features
   - Reference guides when reviewing code
   - Find architectural patterns for common modules

3. **Combine with coding:**
   - "Using the auth guide, generate a login controller"
   - "Following SE best practices, create a payment service"
   - "Based on QA guides, write tests for user registration"

## Alternative: Direct API Access

If MCP setup doesn't work, you can call the REST API directly:

**macOS/Linux:**
```bash
# Get a token:
TOKEN=$(gcloud auth print-identity-token)

# Search for guides:
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 5}' \
  https://mcp-server-375955300575.us-central1.run.app/search | jq

# List divisions:
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions | jq
```

**Windows PowerShell:**
```powershell
# Get a token:
$token = gcloud auth print-identity-token

# Search for guides:
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    query = "authentication"
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://mcp-server-375955300575.us-central1.run.app/search" `
    -Method Post -Headers $headers -Body $body | ConvertTo-Json

# List divisions:
Invoke-RestMethod -Uri "https://mcp-server-375955300575.us-central1.run.app/divisions" `
    -Headers @{"Authorization" = "Bearer $token"} | ConvertTo-Json
```

See [API Reference](api-reference.md) for complete endpoint documentation.

---

**Questions or issues?** Check the troubleshooting section above or run `uv run mcp dev mcp/guides_mcp_server.py` to debug locally.

### 2. `list_guides_by_division`
Lists all guides in a specific division.

**Parameters:**
- `division` (string): pm, qa, se, or exd

**Example:**
```
Show me all the software engineering guides
```

### 3. `get_guide_content`
Retrieves the full content of a specific guide.

**Parameters:**
- `path` (string): Relative path like "se/authentication-module---introduction-1/index.md"

**Example:**
```
Get the authentication module introduction guide for software engineers
```

### 4. `search_guides`
Semantic search across all guides using AI embeddings.

**Parameters:**
- `query` (string): Natural language search query
- `top_k` (integer, optional): Number of results (default: 3, max: 10)

**Example:**
```
Search for guides about user authentication and OAuth
```

### 5. `get_guide_recommendations`
Get personalized guide recommendations.

**Parameters:**
- `topics` (array): List of topics ["auth", "security"]
- `maturity_level` (string, optional): "Introduction 1", "Growth 1", etc.
- `division` (string, optional): pm, qa, se, or exd

**Example:**
```
Recommend guides about authentication and security at the Introduction 1 level for software engineers
```

## Usage Examples

### In Claude Desktop

Once configured, you can ask Claude:

- **"What guide divisions are available?"**
  → Calls `list_guide_divisions`

- **"Show me all SE guides"**
  → Calls `list_guides_by_division` with division="se"

- **"Search for authentication guides"**
  → Calls `search_guides` with query="authentication"

- **"Recommend payment guides at Introduction 1 level"**
  → Calls `get_guide_recommendations` with topics=["payment"], maturity_level="Introduction 1"

Claude automatically selects and executes the appropriate tools.

### Verification

Check that tools are loaded:

1. Look for the 🔧 "Search and tools" icon in Claude Desktop
2. You should see "Implementation Guides" listed
3. 5 tools should be available

## Troubleshooting

### "Command not found" error

Ensure Python is in your PATH:
```bash
which python3
```

Update the config with the full path to Python if needed.

### Authentication errors

Verify your gcloud authentication:
```bash
gcloud auth login
gcloud auth print-identity-token
```

### Connection timeout

The Cloud Run service may take a few seconds to cold start. Wait and retry.

### Tool calls not working

Check the Claude Desktop logs:
- **macOS:** `~/Library/Logs/Claude/mcp*.log`
- **Windows:** `%APPDATA%\Claude\logs\mcp*.log`

## Direct API Access (Alternative)

If MCP setup doesn't work, you can still use the REST API directly:

```bash
# Get auth token
TOKEN=$(gcloud auth print-identity-token)

# Search guides
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

## Architecture

```
┌─────────────────┐
│  Claude / VS    │
│     Code        │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ▼
┌─────────────────┐
│  Local MCP      │
│    Server       │
│ (Python Script) │
└────────┬────────┘
         │ HTTPS + OAuth
         ▼
┌─────────────────┐
│   Cloud Run     │
│   REST API      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vertex AI +    │
│   Firestore     │
└─────────────────┘
```

The MCP server acts as a local bridge, translating MCP protocol calls into REST API requests with proper authentication.

## Security Notes

- Authentication uses your personal gcloud credentials
- The wrapper runs locally on your machine
- No credentials are stored in configuration files
- API calls are authenticated via Google Workspace SSO

## Updating

When the API is updated, simply restart Claude Desktop to pick up changes. No local updates needed since the server calls the live API.
