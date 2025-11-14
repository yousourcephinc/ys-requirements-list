#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
ARGS=()

for arg in "$@"; do
    case "$arg" in
        --json) 
            JSON_MODE=true 
            ;;
        --help|-h) 
            echo "Usage: $0 [--json]"
            echo "  --json    Output results in JSON format"
            echo "  --help    Show this help message"
            exit 0 
            ;;
        *) 
            ARGS+=("$arg") 
            ;;
    esac
done

# Capture raw argument string (used for guide discovery)
PLAN_ARGS="${ARGS[*]}"

# Get script directory and load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get all paths and variables from common functions
eval $(get_feature_paths)

# Check if we're on a proper feature branch (only for git repos)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# Ensure the feature directory exists
mkdir -p "$FEATURE_DIR"

# Copy plan template if it exists
TEMPLATE="$REPO_ROOT/.specify/templates/plan-template.md"
if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$IMPL_PLAN"
    echo "Copied plan template to $IMPL_PLAN"
else
    echo "Warning: Plan template not found at $TEMPLATE"
    # Create a basic plan file if template doesn't exist
    touch "$IMPL_PLAN"
fi

# Discover guide requirements via MCP (with local fallback)
GUIDE_REQUIREMENTS_JSON=$(REPO_ROOT="$REPO_ROOT" \
    FEATURE_SPEC="$FEATURE_SPEC" \
    PLAN_ARGS="$PLAN_ARGS" \
    PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 <<'PY'
import json
import os
import re
from pathlib import Path

from specify_cli.core.mcp_client import ImplementationGuidesMCPClient
from specify_cli.core.guide_requirements import collect_requirements

repo_root = Path(os.environ.get("REPO_ROOT", "."))
spec_path = Path(os.environ.get("FEATURE_SPEC", ""))
plan_args = os.environ.get("PLAN_ARGS", "").strip()

feature_description = plan_args

if spec_path.exists():
    try:
        content = spec_path.read_text(encoding="utf-8")
    except OSError:
        content = ""
    if content:
        match = re.search(r"\*\*Input\*\*:\s*(?:User description:\s*)?\"([^\"]+)\"", content)
        if match:
            feature_description = match.group(1).strip()

mcp_available = False
client = ImplementationGuidesMCPClient(repo_root)
try:
    mcp_available = client.is_available()
except Exception:
    mcp_available = False

requirements = []
source = "none"

if feature_description:
    try:
        requirements = collect_requirements(repo_root, feature_description)
    except Exception:
        requirements = []
    if requirements:
        source = "mcp" if mcp_available else "local"

print(json.dumps({
    "description": feature_description,
    "items": requirements,
    "source": source,
}))
PY
)

if [ -z "$GUIDE_REQUIREMENTS_JSON" ]; then
    GUIDE_REQUIREMENTS_JSON='{"description": "", "items": [], "source": "none"}'
fi

export GUIDE_REQUIREMENTS_JSON

# Output results
if $JSON_MODE; then
    printf '{"FEATURE_SPEC":"%s","IMPL_PLAN":"%s","SPECS_DIR":"%s","BRANCH":"%s","HAS_GIT":"%s","GUIDE_REQUIREMENTS":%s}\n' \
        "$FEATURE_SPEC" "$IMPL_PLAN" "$FEATURE_DIR" "$CURRENT_BRANCH" "$HAS_GIT" "$GUIDE_REQUIREMENTS_JSON"
else
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN" 
    echo "SPECS_DIR: $FEATURE_DIR"
    echo "BRANCH: $CURRENT_BRANCH"
    echo "HAS_GIT: $HAS_GIT"
    GUIDE_SOURCE=$(python3 <<'PY'
import json
import os

data = json.loads(os.environ.get("GUIDE_REQUIREMENTS_JSON", "{}"))
print(data.get("source", "none"))
PY
)
    echo "GUIDE_REQUIREMENTS_SOURCE: $GUIDE_SOURCE"
fi
