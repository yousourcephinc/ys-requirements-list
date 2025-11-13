# Scripts Documentation

This document describes the utility scripts in the `scripts/` directory.

## Overview

The scripts directory contains utilities for:
- Synchronizing content from Notion
- Generating vector embeddings
- Performing semantic search
- Onboarding new guides
- Uploading foundational guides to Notion

## Scripts

### sync_notion.py

Synchronizes implementation guides from Notion to the local repository.

**Purpose**: Daily automated sync from Notion CMS to GitHub repository

**Usage**:
```bash
# Basic sync
python scripts/sync_notion.py

# With specific database ID
python scripts/sync_notion.py --database-id YOUR_DATABASE_ID

# Dry run (preview changes)
python scripts/sync_notion.py --dry-run
```

**Environment Variables**:
- `NOTION_API_KEY` (required): Notion integration API key
- `NOTION_DATABASE_ID` (optional): Override default database

**What it does**:
1. Connects to Notion database
2. Fetches all implementation guides
3. Converts Notion pages to Markdown
4. Organizes by division (SE, EXD, PM, QA)
5. Adds frontmatter with metadata
6. Removes guides deleted in Notion
7. Commits changes to git

**Output**:
```
Syncing guides from Notion...
✓ Found 130 guides
✓ Updated 5 guides
✓ Added 2 new guides
✓ Removed 1 deleted guide
✓ Sync complete
```

**Automation**:
Runs daily at 2 AM UTC via GitHub Actions (`.github/workflows/sync-notion.yml`)

**Troubleshooting**:
```bash
# Check Notion API key
echo $NOTION_API_KEY

# Test connection
python -c "
from scripts.sync_notion import test_connection
test_connection()
"

# View detailed logs
python scripts/sync_notion.py --verbose
```

---

### generate_embeddings.py

Generates vector embeddings for semantic search using Google Vertex AI.

**Purpose**: Create and update semantic search index

**Usage**:
```bash
# Generate embeddings for new/updated guides
python scripts/generate_embeddings.py

# Rebuild entire index (expensive!)
python scripts/generate_embeddings.py --rebuild

# Process specific division
python scripts/generate_embeddings.py --division se

# Dry run (preview)
python scripts/generate_embeddings.py --dry-run
```

**Environment Variables**:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `FIRESTORE_DATABASE`: Firestore database name
- `VERTEX_AI_LOCATION`: Vertex AI region (default: us-central1)

**What it does**:
1. Scans `guides/` directory for markdown files
2. Extracts content and metadata
3. Generates embeddings using Vertex AI
4. Stores vectors in Firestore
5. Creates semantic search index

**Output**:
```
Generating embeddings...
✓ Found 130 guides
✓ Processing se/authentication-module---introduction-1
✓ Generated embedding (768 dimensions)
✓ Stored in Firestore
...
✓ Processed 130 guides in 45s
✓ Cost: ~$0.50
```

**Cost Optimization**:
- Only processes new/updated guides (checks content hash)
- Embeddings cached in Firestore
- Typical cost: $0.50-$2.00 per full rebuild

**Troubleshooting**:
```bash
# Check Vertex AI access
gcloud auth application-default print-access-token

# Test embedding generation
python -c "
from scripts.generate_embeddings import generate_embedding
result = generate_embedding('test content')
print(f'Generated {len(result)} dimensions')
"

# View Firestore documents
gcloud firestore documents list guides \
  --database=implementation-guides \
  --limit=5
```

---

### vector_search.py

Performs semantic search over implementation guides.

**Purpose**: Search guides using natural language queries

**Usage**:
```bash
# Basic search
python scripts/vector_search.py "user authentication OAuth"

# With top_k limit
python scripts/vector_search.py "authentication" --top-k 10

# Filter by division
python scripts/vector_search.py "login" --division se

# Filter by maturity
python scripts/vector_search.py "OAuth setup" --maturity introduction-1

# JSON output
python scripts/vector_search.py "auth" --json
```

**Environment Variables**:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `FIRESTORE_DATABASE`: Firestore database name

**What it does**:
1. Converts query to embedding vector
2. Searches Firestore vector index
3. Ranks results by similarity
4. Applies division/maturity filters
5. Boosts foundational guides
6. Returns top results

**Output**:
```
Searching for: "user authentication OAuth"

Results:
1. Authentication Module - OAuth Integration (se, growth-1)
   Score: 0.92
   Path: se/oauth-integration---growth-1/index.md
   
2. SSO Integration (se, introduction-2)
   Score: 0.87
   Path: se/sso-integration---introduction-2/index.md

Found 2 results in 0.45s
```

**Programmatic Usage**:
```python
from scripts.vector_search import search_guides

results = search_guides(
    query="authentication OAuth",
    top_k=5,
    division="se",
    maturity_level="introduction-1"
)

for result in results:
    print(f"{result['title']} - {result['score']:.2f}")
```

**Troubleshooting**:
```bash
# Test Firestore connection
python -c "
from google.cloud import firestore
db = firestore.Client(database='implementation-guides')
print(list(db.collection('guides').limit(1).stream()))
"

# Check index exists
gcloud firestore indexes list --database=implementation-guides

# Rebuild if no results
python scripts/generate_embeddings.py --rebuild
```

---

### onboard_guide.py

Adds new implementation guides to the repository with proper structure.

**Purpose**: Onboard standalone guides with frontmatter and organization

**Usage**:
```bash
# Single guide
python scripts/onboard_guide.py path/to/guide.md

# Directory of guides
python scripts/onboard_guide.py path/to/guides/

# With parameters (non-interactive)
python scripts/onboard_guide.py guide.md \
  --division se \
  --maturity introduction-1 \
  --title "My New Guide"

# Force update existing guide
python scripts/onboard_guide.py guide.md --force
```

**Interactive Prompts**:
1. **Division**: Select from SE, EXD, PM, QA
2. **Maturity Level**: Select from foundational, introduction-1, etc.
3. **Title**: Auto-generated from filename (editable)

**What it does**:
1. Reads markdown file(s)
2. Prompts for division and maturity (if not provided)
3. Generates slug from title
4. Creates directory structure
5. Adds frontmatter with metadata
6. Copies content to proper location
7. Calculates content hash for change detection

**Output**:
```
Onboarding guide: api-best-practices.md

Division: se (Software Engineering)
Maturity: introduction-1
Title: API Controller Best Practices

Creating: guides/se/api-controller-best-practices---introduction-1/index.md
✓ Guide created successfully

Next steps:
1. Review the guide at guides/se/...
2. Run: python scripts/generate_embeddings.py
3. Commit and push changes
```

**Directory Structure Created**:
```
guides/
└── se/
    └── api-controller-best-practices---introduction-1/
        └── index.md
```

**Frontmatter Added**:
```markdown
---
title: API Controller Best Practices
division: se
maturity: introduction-1
created_at: '2025-11-13T10:30:00'
content_hash: 664624f6097367ba31ea936b6b57f2de
---

# API Controller Best Practices
...
```

**Batch Processing**:
```bash
# Process all guides in staging directory
python scripts/onboard_guide.py ~/staging/

# The script will:
# 1. Find all .md files
# 2. Prompt for division/maturity once
# 3. Show preview table
# 4. Process all files
```

**Troubleshooting**:
```bash
# Check for frontmatter module
pip install python-frontmatter

# Test file processing
python -c "
from scripts.onboard_guide import process_guide
process_guide('test.md', division='se', maturity='introduction-1', title='Test')
"
```

---

### upload_foundational_to_notion.py

Uploads local foundational guides to Notion database.

**Purpose**: Sync foundational guides from local files to Notion CMS

**Usage**:
```bash
# Upload all foundational guides
python scripts/upload_foundational_to_notion.py

# Upload specific division
python scripts/upload_foundational_to_notion.py --division se

# Dry run
python scripts/upload_foundational_to_notion.py --dry-run

# Update existing guides
python scripts/upload_foundational_to_notion.py --update
```

**Environment Variables**:
- `NOTION_API_KEY` (required): Notion integration API key
- `NOTION_DATABASE_ID` (optional): Target database

**What it does**:
1. Scans `guides/` for foundational guides
2. Converts Markdown to Notion blocks
3. Uploads to Notion database
4. Sets proper properties (division, maturity, title)
5. Links to source file

**Output**:
```
Uploading foundational guides to Notion...
✓ Found 15 foundational guides
✓ Uploading se/security-best-practices---foundational
✓ Created page: https://notion.so/...
...
✓ Uploaded 15 guides
```

**Limitations**:
- Only uploads guides with `maturity: foundational`
- Requires Notion integration with write permissions
- Complex Markdown may need manual adjustment

**Troubleshooting**:
```bash
# Test Notion connection
python -c "
from notion_client import Client
notion = Client(auth=os.environ['NOTION_API_KEY'])
print(notion.users.me())
"

# Check database permissions
python -c "
from notion_client import Client
notion = Client(auth=os.environ['NOTION_API_KEY'])
db = notion.databases.retrieve(database_id='YOUR_DB_ID')
print(db['properties'])
"
```

---

## Common Workflows

### Adding a New Guide

```bash
# 1. Create or receive markdown file
vim new-guide.md

# 2. Onboard the guide
python scripts/onboard_guide.py new-guide.md

# 3. Generate embeddings
python scripts/generate_embeddings.py

# 4. Test search
python scripts/vector_search.py "keywords from guide"

# 5. Commit
git add guides/
git commit -m "docs: add new implementation guide"
git push
```

### Syncing from Notion

```bash
# 1. Sync guides
python scripts/sync_notion.py

# 2. Review changes
git diff

# 3. Generate embeddings for new/updated
python scripts/generate_embeddings.py

# 4. Commit changes
git add .
git commit -m "docs: sync from Notion"
git push
```

### Rebuilding Search Index

```bash
# 1. Backup current index (optional)
gcloud firestore export gs://backup-bucket/firestore-backup

# 2. Rebuild embeddings
python scripts/generate_embeddings.py --rebuild

# 3. Test search
python scripts/vector_search.py "test query"

# 4. Verify count
python -c "
from google.cloud import firestore
db = firestore.Client(database='implementation-guides')
count = len(list(db.collection('guides').stream()))
print(f'Index has {count} documents')
"
```

## Automation

### GitHub Actions

All scripts can run via GitHub Actions:

**Daily Notion Sync** (`.github/workflows/sync-notion.yml`):
```yaml
- name: Sync from Notion
  run: python scripts/sync_notion.py
  env:
    NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
```

**Generate Embeddings** (`.github/workflows/generate-embeddings.yml`):
```yaml
- name: Generate embeddings
  run: python scripts/generate_embeddings.py
  env:
    GOOGLE_CLOUD_PROJECT: ${{ secrets.GCP_PROJECT_ID }}
```

### Cron Jobs

For local automation:

```bash
# Add to crontab (crontab -e)

# Sync from Notion daily at 2 AM
0 2 * * * cd /path/to/repo && python scripts/sync_notion.py

# Generate embeddings after sync
0 3 * * * cd /path/to/repo && python scripts/generate_embeddings.py
```

## Environment Setup

Required for all scripts:

```bash
# Create .env file
cat > .env << EOF
NOTION_API_KEY=your_notion_api_key
GOOGLE_CLOUD_PROJECT=implementation-guides-439017
FIRESTORE_DATABASE=implementation-guides
VERTEX_AI_LOCATION=us-central1
EOF

# Load environment
source .env

# Or use direnv
echo "dotenv" > .envrc
direnv allow
```

## Dependencies

All scripts require:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `notion-client` - Notion API
- `google-cloud-firestore` - Firestore
- `google-cloud-aiplatform` - Vertex AI
- `python-frontmatter` - Frontmatter parsing
- `click` - CLI framework

## Related Documentation

- [Local Development Guide](local-development.md)
- [API Reference](api-reference.md)
- [Configuration Reference](configuration.md)
- [Troubleshooting](troubleshooting.md)

---

**Last Updated**: November 13, 2025
