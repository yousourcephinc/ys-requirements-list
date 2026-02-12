#!/usr/bin/env bash
# YS Guides plugin - prerequisite check (runs on SessionStart)
# Checks: gcloud CLI, Python 3.10+, pip packages, Google Cloud auth
set -euo pipefail

MCP_URL="https://mcp-server-375955300575.us-central1.run.app/mcp"
STATUS="ready"
MESSAGES=()

# ── 1. gcloud CLI ──────────────────────────────────────────────
if ! command -v gcloud &>/dev/null; then
  STATUS="blocked"
  MESSAGES+=("MISSING_GCLOUD: The gcloud CLI is not installed. Install it from https://cloud.google.com/sdk/docs/install then restart Claude.")
fi

# ── 2. Python 3.10+ ───────────────────────────────────────────
if command -v python3 &>/dev/null; then
  py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  py_major=$(echo "$py_version" | cut -d. -f1)
  py_minor=$(echo "$py_version" | cut -d. -f2)
  if [ "$py_major" -lt 3 ] || { [ "$py_major" -eq 3 ] && [ "$py_minor" -lt 10 ]; }; then
    STATUS="blocked"
    MESSAGES+=("PYTHON_TOO_OLD: Python 3.10+ is required but found $py_version.")
  fi
else
  STATUS="blocked"
  MESSAGES+=("MISSING_PYTHON: Python 3 is not installed.")
fi

# ── 3. Pip packages ───────────────────────────────────────────
missing_pkgs=()
python3 -c "import httpx" 2>/dev/null || missing_pkgs+=("httpx")
python3 -c "import google.auth" 2>/dev/null || missing_pkgs+=("google-auth" "google-auth-httplib2")

if [ ${#missing_pkgs[@]} -gt 0 ]; then
  echo "Installing missing Python packages: ${missing_pkgs[*]}"
  if pip install "${missing_pkgs[@]}" 2>&1; then
    echo "Packages installed successfully."
  else
    STATUS="blocked"
    MESSAGES+=("PIP_INSTALL_FAILED: Could not install ${missing_pkgs[*]}. Run manually: pip install ${missing_pkgs[*]}")
  fi
fi

# ── 4. Google Cloud authentication ────────────────────────────
if [ "$STATUS" != "blocked" ]; then
  if ! gcloud auth print-identity-token --audiences="$MCP_URL" &>/dev/null; then
    STATUS="auth_needed"
    MESSAGES+=("AUTH_NEEDED: Google Cloud authentication is required. Run 'gcloud auth login' to authenticate (this will open your browser).")
  fi
fi

# ── Output ─────────────────────────────────────────────────────
if [ "$STATUS" = "ready" ]; then
  echo "YS_GUIDES_READY: All prerequisites met. The ys-guides MCP server is ready to use."
else
  for msg in "${MESSAGES[@]}"; do
    echo "$msg"
  done
fi
