# Setup Guide for Automated Notion Sync

## Current Status ✅

Your repository is now configured for automated Notion syncing with the following:

### Files Created:
- ✅ `.github/workflows/sync.yml` - GitHub Action for automated syncing
- ✅ `.gitignore` - Already configured to ignore `.env` and cache files
- ✅ `sync_notion.py` - Script that syncs from Notion with toggle support
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env` - Local environment variables (not committed to Git)

### Features:
- **Daily automatic sync** at 2 AM UTC
- **Manual trigger** available via GitHub Actions UI
- **Toggle content support** - Captures nested content in Notion toggles
- **Division-based organization** - Files organized by PM/QA/SE/EXD divisions
- **Smart updates** - Only updates changed files, skips unchanged ones
- **Semantic search** - AI-powered search using embeddings and vector similarity
- **Cleanup** - Removes files that no longer exist in Notion

## Next Steps

### 1. Push to GitHub

First, commit and push your changes:

\`\`\`bash
git add .
git commit -m "feat: Add automated Notion sync workflow"
git push origin main
\`\`\`

### 2. Configure GitHub Secrets

Go to your GitHub repository: `https://github.com/yousourcephinc/ys-requirements-list`

Navigate to: **Settings** → **Secrets and variables** → **Actions**

Click **New repository secret** and add the following three secrets:

#### Secret 1: NOTION_API_KEY
- **Name:** `NOTION_API_KEY`
- **Value:** `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`

#### Secret 2: NOTION_DATABASE_ID
- **Name:** `NOTION_DATABASE_ID`
- **Value:** `12aa172b65a380048ed7c2f9ee5e1bfe`

#### Secret 3: NOTION_VIEW_ID
- **Name:** `NOTION_VIEW_ID`
- **Value:** `1aea172b65a3801e8f5b000c48917d78`

### 3. Test the Workflow

Once secrets are configured:

1. Go to the **Actions** tab in your GitHub repository
2. Click on **Sync Guides from Notion** workflow
3. Click **Run workflow** button (top right)
4. Select the `main` branch
5. Click **Run workflow**

The workflow will:
- Check out your code
- Install Python dependencies
- Run the sync script
- Commit and push any changes back to the repository

### 4. Monitor the Workflow

After triggering:
- Watch the workflow run in real-time
- Check for any errors in the logs
- Verify that new commits appear with message: "docs(guides): Sync guides from Notion [skip ci]"

## Workflow Schedule

The workflow runs automatically:
- **Daily at 2:00 AM UTC** (6:00 PM PST / 7:00 PM PDT)
- **On-demand** via the "Run workflow" button

## Troubleshooting

### If the workflow fails:

1. **Check secrets are configured correctly** - Go to Settings → Secrets
2. **View workflow logs** - Click on the failed run to see detailed error messages
3. **Test locally first** - Run `python3 sync_notion.py` locally to verify it works
4. **Check Notion permissions** - Ensure the integration has access to your database

### Common Issues:

- **Authentication Error**: Check that `NOTION_API_KEY` is correct
- **Database Not Found**: Verify `NOTION_DATABASE_ID` matches your database
- **No Changes Detected**: This is normal if Notion content hasn't changed

## Repository Structure

After sync, your repository will look like:

\`\`\`
ys-requirements-list/
├── .github/
│   └── workflows/
│       └── sync.yml
├── guides/
│   ├── README.md          # Auto-generated catalog
│   ├── semantic_index/    # AI search index (generated)
│   │   ├── guides.index   # FAISS vector index
│   │   ├── metadata.json  # Search metadata
│   │   └── documents.json # Document chunks
│   ├── pm/                # PM division guides
│   ├── qa/                # QA division guides
│   ├── se/                # SE division guides
│   └── exd/               # EXD division guides
├── .env                   # Local only (not in Git)
├── .gitignore
├── requirements.txt
├── sync_notion.py
├── test_semantic_search.py
└── README.md
\`\`\`

## Semantic Search

Your repository now includes AI-powered semantic search! After each sync, the system automatically:

1. **Chunks** all guide content into searchable segments
2. **Generates embeddings** using sentence transformers
3. **Creates FAISS index** for fast similarity search
4. **Enables natural language queries** like "authentication setup" or "database patterns"

### Testing Semantic Search

Run the test script locally:

\`\`\`bash
python test_semantic_search.py "authentication setup"
python test_semantic_search.py "API security best practices"
python test_semantic_search.py "database design patterns"
\`\`\`

### How It Works

- **Model**: Uses `all-MiniLM-L6-v2` for fast, high-quality embeddings
- **Similarity**: Cosine similarity for semantic matching
- **Chunking**: 500-word chunks with 50-word overlap for context
- **Storage**: FAISS index for sub-second search on 1000+ documents

## Updating the Workflow

To change the sync schedule, edit `.github/workflows/sync.yml`:

\`\`\`yaml
schedule:
  - cron: '0 2 * * *'  # Change this cron expression
\`\`\`

Cron examples:
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * *'` - Daily at midnight
- `'0 9 * * 1-5'` - Weekdays at 9 AM

## Success Indicators

✅ Workflow runs without errors
✅ New commits appear automatically
✅ `guides/` directory stays up-to-date with Notion
✅ README.md catalog is regenerated
✅ Only changed files are updated
