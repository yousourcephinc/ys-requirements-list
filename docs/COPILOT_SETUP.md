# GitHub Copilot MCP Setup Guide

Connect GitHub Copilot in VS Code to your company's implementation guides using the MCP (Model Context Protocol) server. This setup takes about 5 minutes.

## What You'll Get

Once configured, GitHub Copilot can:
- **Search implementation guides** - "Search for authentication patterns"
- **Get specific requirements** - "Show me the payment module guide"
- **List available guides** - "What SE guides exist?"
- **Find recommendations** - "Recommend guides for user management"

All responses will reference your company's actual implementation standards instead of generic internet knowledge.

## How It Works

```
VS Code with Copilot
    │
    ▼
Local MCP Server (HTTP)
    │ (runs on localhost:8080)
    ▼
Google Cloud Run API
    │ (with your gcloud auth)
    ▼
Firestore + Vertex AI
    (130+ implementation guides)
```

The local server bridges GitHub Copilot's MCP protocol to the Cloud Run API using your authenticated gcloud credentials.

## Prerequisites

1. **Visual Studio Code** with **GitHub Copilot** extension installed
2. **Google Cloud SDK** authenticated with `@you-source.com` account
3. **Python 3.10+** installed on your system
4. **This repository cloned** locally

## Quick Setup (3 Steps)

### Step 1: Authenticate with Google Cloud

**macOS/Linux:**
```bash
# Login with your @you-source.com account:
gcloud auth login

# Verify authentication:
gcloud auth print-identity-token
# Should output a long JWT token starting with "eyJ..."
```

**Windows PowerShell:**
```powershell
# Login with your @you-source.com account:
gcloud auth login

# Verify authentication:
gcloud auth print-identity-token
# Should output a long JWT token starting with "eyJ..."
```

### Step 2: Start the Local MCP Server

The MCP server needs to run locally to bridge GitHub Copilot to the Cloud Run API.

**macOS/Linux:**
```bash
# Navigate to the repository:
cd ~/code/ys-requirements-list

# Start the HTTP server (runs on port 8080):
python mcp/guides_mcp_http_server.py
```

**Windows PowerShell:**
```powershell
# Navigate to the repository:
cd $env:USERPROFILE\code\ys-requirements-list

# Start the HTTP server (runs on port 8080):
python mcp/guides_mcp_http_server.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:8080
 * MCP endpoint available at: http://127.0.0.1:8080/mcp
 * Press CTRL+C to quit
```

**Keep this terminal running** - the server must stay active while using Copilot.

### Step 3: Configure VS Code

**Option A: Automatic Setup (Recommended)**

If you initialized your project with `specify init --ai copilot`, the configuration is already created at `.vscode/settings.json`.

**Option B: Manual Setup**

Create or edit `.vscode/settings.json` in your project root:

**macOS/Linux/Windows (same configuration):**
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

**Save the file**, then reload VS Code:
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type "Developer: Reload Window"
- Press Enter

## Verify It's Working

### Check 1: Server Health

Test the local server directly:

**macOS/Linux:**
```bash
curl http://127.0.0.1:8080/health
# Should return: {"status": "healthy"}
```

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8080/health"
# Should return: status : healthy
```

### Check 2: MCP Endpoint

Test the MCP endpoint:

**macOS/Linux:**
```bash
curl http://127.0.0.1:8080/mcp
# Should return JSON with available tools
```

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8080/mcp"
# Should return JSON with available tools
```

### Check 3: GitHub Copilot

Open Copilot Chat in VS Code and ask:

```
@workspace What guide divisions are available?
```

**Expected:** Copilot should use the MCP server and return:
```
I found 4 divisions:
- PM (Product Management): 25 guides
- QA (Quality Assurance): 30 guides
- SE (Software Engineering): 70 guides
- EXD (Experience Design): 15 guides
```

If it doesn't work, check the **Troubleshooting** section below.

## Using GitHub Copilot with Guides

Always start queries with `@workspace` to give Copilot access to the MCP tools.

### Natural Language Examples

| What You Ask | What Copilot Does |
|--------------|-------------------|
| `@workspace What guide divisions exist?` | Calls `list_guide_divisions` |
| `@workspace Show me all SE guides` | Calls `list_guides_by_division("se")` |
| `@workspace Search for authentication guides` | Calls `search_guides("authentication")` |
| `@workspace Get the auth module guide` | Calls `get_guide_content(...)` |
| `@workspace Recommend payment guides` | Calls `get_guide_recommendations(...)` |

You don't need to know tool names - just ask naturally!

### Example Workflows

#### 1. Starting a New Feature
```
You: @workspace I need to build a notification system. 
     What guides are available?

Copilot: [Searches guides]
         I found these notification guides:
         - SE/Notification System - Introduction 1
         - SE/Email Notifications - Growth 1
         - QA/Notification Testing - Introduction 2
         
         Would you like me to show you the requirements 
         from any of these?
```

#### 2. Implementing with Guide Reference
```
You: @workspace Based on the SE notification guide at 
     Introduction 1 level, create a Python notification service

Copilot: [Fetches guide content]
         [Generates code following your company's standards]
         
         Here's a notification service that follows your 
         implementation guide:
         
         ```python
         # Includes your required patterns
         # Uses your approved libraries
         # Follows your security checklist
         ```
```

#### 3. Code Review with Standards
```
You: @workspace Review this payment code against our 
     payment module guides

Copilot: [Searches payment guides]
         [Compares code to requirements]
         
         Based on your SE Payment Module guide, I notice:
         - ✅ Using approved payment gateway (Stripe)
         - ❌ Missing PCI compliance logging
         - ❌ Missing required error handling pattern
         
         Here's the updated code...
```

## Troubleshooting

### ❌ Server won't start

**Problem:** `python mcp/guides_mcp_http_server.py` fails.

**Fix:**
```bash
# Install dependencies:
pip install flask httpx google-cloud-firestore google-cloud-aiplatform

# Or use uv:
cd ~/code/ys-requirements-list
uv pip install -r requirements.txt
```

### ❌ "Port 8080 already in use"

**Problem:** Another process is using port 8080.

**Fix (macOS/Linux):**
```bash
# Find process using port 8080:
lsof -ti:8080

# Kill it:
kill $(lsof -ti:8080)

# Or use different port:
PORT=8081 python mcp/guides_mcp_http_server.py

# Update .vscode/settings.json URL to match
```

**Fix (Windows PowerShell):**
```powershell
# Find process using port 8080:
Get-NetTCPConnection -LocalPort 8080 | Select-Object OwningProcess

# Kill it (replace PID):
Stop-Process -Id <PID>

# Or use different port:
$env:PORT = 8081
python mcp/guides_mcp_http_server.py

# Update .vscode/settings.json URL to match
```

### ❌ "Authentication failed" errors in server logs

**Problem:** gcloud not authenticated.

**Fix:**
```bash
# Re-authenticate:
gcloud auth login

# Verify:
gcloud auth print-identity-token

# Restart the server
```

### ❌ Copilot doesn't respond or says "no tools available"

**Problem:** VS Code hasn't loaded the MCP configuration.

**Fix:**
1. Verify `.vscode/settings.json` exists and contains the MCP config
2. Reload VS Code window (`Cmd+Shift+P` → "Developer: Reload Window")
3. Check server is running: `curl http://127.0.0.1:8080/health`
4. Enable verbose logging:
   - `Cmd+Shift+P` → "GitHub Copilot: Enable Debug Output"
   - Check Output panel for MCP connection logs

### ❌ "Connection refused" errors

**Problem:** Local server not running or wrong URL.

**Fix:**
1. Check server is running: `curl http://127.0.0.1:8080/health`
2. Verify URL in `.vscode/settings.json` is `http://127.0.0.1:8080/mcp`
3. Ensure no firewall blocking localhost:8080
4. Try restarting the server

### ❌ Server logs show "Guide not found" errors

**Problem:** Server can't find guide files.

**Fix:**
```bash
# Verify guides directory exists:
ls guides/

# Should show: pm/, qa/, se/, exd/ directories

# If missing, you're in wrong directory:
cd ~/code/ys-requirements-list
python mcp/guides_mcp_http_server.py
```

## Running Server in Background

To keep the server running without blocking your terminal:

**macOS/Linux:**
```bash
# Run in background:
python mcp/guides_mcp_http_server.py > /tmp/mcp-server.log 2>&1 &

# Check it's running:
curl http://127.0.0.1:8080/health

# View logs:
tail -f /tmp/mcp-server.log

# Stop it later:
pkill -f guides_mcp_http_server
```

**Windows PowerShell:**
```powershell
# Run in new window:
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python mcp/guides_mcp_http_server.py"

# Check it's running:
Invoke-RestMethod -Uri "http://127.0.0.1:8080/health"

# Stop it: Close the PowerShell window or Ctrl+C in that window
```

## Advanced: Auto-Start on Login

**macOS (using launchd):**

Create `~/Library/LaunchAgents/com.yoursource.mcp-server.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yoursource.mcp-server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/code/ys-requirements-list/mcp/guides_mcp_http_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/mcp-server.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mcp-server-error.log</string>
</dict>
</plist>
```

Update `YOUR_USERNAME` and load:
```bash
launchctl load ~/Library/LaunchAgents/com.yoursource.mcp-server.plist
```

**Windows (using Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task → Name: "MCP Server"
3. Trigger: "At log on"
4. Action: "Start a program"
5. Program: `python`
6. Arguments: `C:\Users\YOUR_USERNAME\code\ys-requirements-list\mcp\guides_mcp_http_server.py`
7. Start in: `C:\Users\YOUR_USERNAME\code\ys-requirements-list`
8. Finish

**Linux (using systemd):**

Create `~/.config/systemd/user/mcp-server.service`:

```ini
[Unit]
Description=MCP Implementation Guides Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/YOUR_USERNAME/code/ys-requirements-list
ExecStart=/usr/bin/python3 mcp/guides_mcp_http_server.py
Restart=always

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable mcp-server
systemctl --user start mcp-server
systemctl --user status mcp-server
```

## Alternative: Using specify init

If you're starting a new project, the easiest way is:

```bash
specify init --ai copilot --script sh
```

This automatically:
- ✅ Creates `.vscode/settings.json` with MCP configuration
- ✅ Sets up proper GitHub Copilot integration
- ✅ Configures the local server URL

See [specify documentation](../../ys-spec-kit/README.md) for details.

## Available MCP Tools

GitHub Copilot automatically selects the right tool based on your question:

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `list_guide_divisions` | List all divisions (PM, QA, SE, EXD) | "What divisions exist?" |
| `list_guides_by_division` | List guides in specific division | "Show SE guides" |
| `get_guide_content` | Fetch full guide content | "Get auth guide" |
| `search_guides` | Semantic search across guides | "Find OAuth guides" |
| `get_guide_recommendations` | Get personalized recommendations | "Recommend payment guides" |

## Architecture Details

```
┌─────────────────────┐
│   VS Code with      │  You: "@workspace Search for auth"
│  GitHub Copilot     │
└──────────┬──────────┘
           │ MCP Protocol
           ▼
┌─────────────────────┐
│  Local HTTP Server  │  http://127.0.0.1:8080/mcp
│ guides_mcp_http_    │  Translates MCP → REST API
│    server.py        │  Gets gcloud token
└──────────┬──────────┘
           │ HTTPS + Google OAuth
           ▼
┌─────────────────────┐
│  Cloud Run API      │  Production service
│ (Google Cloud)      │  Validates token
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Firestore +         │  Semantic search
│ Vertex AI           │  130+ guides
└─────────────────────┘
```

**Key Points:**
- Local server runs on your machine (port 8080)
- Uses your personal gcloud credentials
- Calls production Cloud Run API
- No API keys stored in config files
- Real-time semantic search

## Security & Privacy

✅ **Credentials stay local** - Your gcloud auth never leaves your machine  
✅ **Temporary tokens** - Identity tokens expire in 1 hour  
✅ **Domain-restricted** - Only `@you-source.com` accounts work  
✅ **Audit trail** - All API calls logged in Cloud Run  
✅ **Open source** - You can inspect the server code  

## Related Documentation

- [MCP Setup Guide](MCP_SETUP.md) - Setup for Claude Desktop
- [API Reference](api-reference.md) - Direct REST API usage
- [Local Development](local-development.md) - Running servers locally
- [Troubleshooting](troubleshooting.md) - Common issues across tools

---

**Questions or issues?** Check the troubleshooting section above or see the [full troubleshooting guide](troubleshooting.md).