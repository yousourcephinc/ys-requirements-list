# Setup Guide for Automated Notion Sync

## Current Status ✅

Your repository is configured for automated Notion syncing with the following:

### Files Created:
- ✅ `.github/workflows/main.yml` - GitHub Action for automated syncing
- ✅ `.github/workflows/deploy.yml` - GitHub Action for Cloud Run deployment
- ✅ `.gitignore` - Configured to ignore `.env` and cache files
- ✅ `sync_notion.py` - Script that syncs from Notion with toggle support
- ✅ `guides_mcp_api.py` - REST API server deployed on Cloud Run
- ✅ `vector_search.py` - Vertex AI embeddings + Firestore vector search
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env` - Local environment variables (not committed to Git)

### Features:
- **Daily automatic sync** at 2 AM UTC from Notion to GitHub
- **Manual trigger** available via GitHub Actions UI
- **Toggle content support** - Captures nested content in Notion toggles
- **Division-based organization** - Files organized by PM/QA/SE/EXD divisions
- **Smart updates** - Only updates changed files, skips unchanged ones
- **AI-powered semantic search** - Google Vertex AI text-embedding-004 model
- **Vector storage** - Firestore Native database with similarity search
- **Cloud deployment** - Scale-to-zero Cloud Run service
- **Cleanup** - Removes files that no longer exist in Notion

## Next Steps

### 1. Verify GitHub Secrets

Your GitHub secrets should already be configured at:
`https://github.com/yousourcephinc/ys-requirements-list/settings/secrets/actions`

Required secrets:
- `NOTION_API_KEY` - Your Notion integration API key
- `NOTION_DATABASE_ID` - Your Notion database ID
- `NOTION_VIEW_ID` - Your Notion view ID
- `GCP_SA_KEY` - Google Cloud service account key (JSON)

⚠️ **Never commit these values to the repository**

### 2. Test the Notion Sync Workflow

Once secrets are configured:

1. Go to the **Actions** tab in your GitHub repository
2. Click on **Sync Guides from Notion** workflow
3. Click **Run workflow** button (top right)
4. Select the `main` branch
5. Click **Run workflow**

The workflow will:
- Check out your code
- Install Python dependencies (notion-client, python-dotenv only)
- Run the sync script
- Commit and push any changes back to the repository

### 3. Monitor the Workflow

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

1. **Check secrets are configured correctly** - Go to Settings -> Secrets
2. **View workflow logs** - Click on the failed run to see detailed error messages
3. **Test locally first** - Run `python3 sync_notion.py` locally to verify it works
4. **Check Notion permissions** - Ensure the integration has access to your database

### Common Issues:

- **Authentication Error**: Check that `NOTION_API_KEY` is correct
- **Database Not Found**: Verify `NOTION_DATABASE_ID` matches your database
- **No Changes Detected**: This is normal if Notion content hasn't changed

## Repository Structure

After sync, your repository will look like:

```
ys-requirements-list/
├── .github/
│   └── workflows/
│       ├── main.yml        # Notion sync workflow
│       └── deploy.yml      # Cloud Run deployment
├── guides/
│   ├── README.md          # Auto-generated catalog
│   ├── pm/                # PM division guides
│   ├── qa/                # QA division guides
│   ├── se/                # SE division guides
│   └── exd/               # EXD division guides
├── .env                   # Local only (not in Git)
├── .gitignore
├── guides_mcp_api.py      # REST API server
├── vector_search.py       # Vertex AI + Firestore search
├── sync_notion.py         # Notion sync script
├── requirements.txt
├── Dockerfile             # Cloud Run container
└── README.md
```

## Cloud Deployment

### Production Service

**URL**: https://mcp-server-375955300575.us-central1.run.app
**Authentication**: Google Workspace (domain:you-source.com)
**Platform**: Google Cloud Run (us-central1)
**Configuration**: 
- Scale: 0-5 instances
- Memory: 2Gi
- CPU: 1
- Budget: $20 USD max

### Semantic Search Architecture

The deployed service uses:

1. **Vertex AI** - Google's text-embedding-004 model for generating embeddings
   - Cost: ~$0.00002 per 1,000 characters
   - Fast, high-quality embeddings
   
2. **Firestore** - Native mode for vector storage
   - Cosine similarity search
   - 130 guides indexed
   - Free tier enabled

3. **Cloud Run** - Serverless container platform
   - Automatic scaling (including to zero)
   - No cold start issues with managed services

### Testing the Deployed API

```bash
# Health check
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/health

# List divisions
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/divisions

# Semantic search
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication setup", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

## Updating the Workflow

To change the sync schedule, edit `.github/workflows/main.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Change this cron expression
```

Cron examples:
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * *'` - Daily at midnight
- `'0 9 * * 1-5'` - Weekdays at 9 AM

## Cost Management

### Budget Alerts
- **Limit**: $20 USD per month
- **Alerts**: 50%, 75%, 90%, 100% thresholds
- **Action**: Email notifications to billing admins

### Resource Quotas
- **Cloud Run**: Max 5 instances (0-5 autoscaling)
- **Memory**: 2Gi per instance
- **Timeout**: 300 seconds
- **Vertex AI**: Pay-per-use embedding generation

View current spending: https://console.cloud.google.com/billing

## Success Indicators

✅ Workflow runs without errors
✅ New commits appear automatically with "[skip ci]" message
✅ `guides/` directory stays up-to-date with Notion
✅ README.md catalog is regenerated
✅ Only changed files are updated
✅ Cloud Run service responds to API requests
✅ Semantic search returns relevant results
