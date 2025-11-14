#!/usr/bin/env bash
"""
Save and deploy script for ys-spec-kit.

This script automates the version sync, commit, and tag deployment process.

Usage:
  ./scripts/savedeploy.sh [patch|minor|major]

Arguments:
  patch  Increment patch version (0.1.2 -> 0.1.3)
  minor  Increment minor version (0.1.2 -> 0.2.0)
  major  Increment major version (0.1.2 -> 1.0.0)

Prerequisites:
  - CHANGELOG.md must be updated with release notes
  - All changes must be committed except version updates
"""

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to increment version
increment_version() {
    local version=$1
    local bump_type=$2

    # Split version into components
    IFS='.' read -ra VERSION_PARTS <<< "$version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}

    case $bump_type in
        patch)
            patch=$((patch + 1))
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        *)
            log_error "Invalid bump type: $bump_type. Use patch, minor, or major."
            exit 1
            ;;
    esac

    echo "$major.$minor.$patch"
}

# Function to update version in file
update_version_in_file() {
    local file=$1
    local old_version=$2
    local new_version=$3

    if [[ "$file" == *"pyproject.toml" ]]; then
        # Update pyproject.toml
        sed -i.bak "s/^version = \"$old_version\"/version = \"$new_version\"/" "$file"
    elif [[ "$file" == *"package.json" ]]; then
        # Update package.json
        sed -i.bak "s/\"version\": \"$old_version\"/\"version\": \"$new_version\"/" "$file"
    fi

    rm -f "${file}.bak"
}

# Parse arguments
BUMP_TYPE=${1:-patch}

if [[ "$BUMP_TYPE" != "patch" && "$BUMP_TYPE" != "minor" && "$BUMP_TYPE" != "major" ]]; then
    log_error "Invalid argument: $BUMP_TYPE"
    echo "Usage: $0 [patch|minor|major]"
    echo "Default: patch"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff --quiet || ! git diff --staged --quiet; then
    log_error "There are uncommitted changes. Please commit all changes before running this script."
    log_info "Use 'git status' to see what needs to be committed."
    exit 1
fi

cd "$REPO_ROOT"

# Read current version from pyproject.toml
CURRENT_VERSION=$(python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
match = re.search(r'^version\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+)\"', content, re.MULTILINE)
if match:
    print(match.group(1))
else:
    exit(1)
")

if [ -z "$CURRENT_VERSION" ]; then
    log_error "Could not read version from pyproject.toml"
    exit 1
fi

# Calculate new version
NEW_VERSION=$(increment_version "$CURRENT_VERSION" "$BUMP_TYPE")

log_info "Current version: $CURRENT_VERSION"
log_info "Bump type: $BUMP_TYPE"
log_info "New version: $NEW_VERSION"

# Update versions in both files
log_info "Updating version files..."
update_version_in_file "pyproject.toml" "$CURRENT_VERSION" "$NEW_VERSION"
update_version_in_file "package.json" "$CURRENT_VERSION" "$NEW_VERSION"

# Commit version updates
log_info "Committing version updates..."
git add pyproject.toml package.json
git commit -m "chore: bump version to $NEW_VERSION"
log_success "Version update committed"

# Create and push tag
TAG_NAME="v$NEW_VERSION"
log_info "Creating tag $TAG_NAME..."

if git tag -l | grep -q "^$TAG_NAME$"; then
    log_warning "Tag $TAG_NAME already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Tag creation cancelled"
        exit 0
    fi
    git tag -d "$TAG_NAME"
    log_info "Deleted existing tag $TAG_NAME"
fi

git tag "$TAG_NAME"
log_success "Created tag $TAG_NAME"

# Push commits and tags
log_info "Pushing changes and tags..."
git push origin main
git push origin "$TAG_NAME"

log_success "Deployment complete!"
log_info "GitHub Actions will now build and release version $NEW_VERSION"
log_info "Monitor the release at: https://github.com/yousourcephinc/ys-spec-kit/actions"