# Cloud Deployment Guide

This guide covers deploying the Guides REST API to Google Cloud Run.

## Architecture Overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Notion    │────▶│  GitHub Actions  │────▶│  Git Repository │
│  Database   │     │  (Daily Sync)    │     │     (guides/)   │
└─────────────┘     └──────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                        │
│                                                                  │
│  ┌──────────────┐   ┌─────────────┐   ┌──────────────────┐    │
│  │  Cloud Build │──▶│  Cloud Run  │◀─▶│  Secret Manager  │    │
│  │  (Docker)    │   │  (API)      │   │  (Notion Keys)   │    │
│  └──────────────┘   └─────────────┘   └──────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│         ┌──────────────────────────────────┐                   │
│         │      Vertex AI + Firestore       │                   │
│         │  (Embeddings + Vector Search)    │                   │
│         └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- GitHub repository with Actions enabled
- Notion API integration created

## Initial Setup

### 1. Create GCP Project

```bash
# Create project
gcloud projects create requirements-mcp-server --name="Requirements MCP Server"

# Set as active project
gcloud config set project requirements-mcp-server

# Enable billing (must be done via console)
# https://console.cloud.google.com/billing
```

### 2. Enable Required APIs

```bash
# Enable all necessary APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  billingbudgets.googleapis.com
```

### 3. Create Firestore Database

```bash
# Create Firestore in Native mode
gcloud firestore databases create \
  --location=us-central1 \
  --type=firestore-native
```

### 4. Configure Secrets

```bash
# Store Notion API key
echo -n "secret_your_notion_api_key" | \
  gcloud secrets create notion-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Store Notion Database ID
echo -n "your_database_id" | \
  gcloud secrets create notion-database-id \
    --data-file=- \
    --replication-policy="automatic"
```

### 5. Set Up Service Account Permissions

```bash
# Get the compute service account email
PROJECT_NUMBER=$(gcloud projects describe requirements-mcp-server --format="value(projectNumber)")
SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant required permissions
gcloud projects add-iam-policy-binding requirements-mcp-server \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding requirements-mcp-server \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding requirements-mcp-server \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user"
```

### 6. Configure Budget Alerts

```bash
# Get billing account
BILLING_ACCOUNT=$(gcloud billing projects describe requirements-mcp-server \
  --format="value(billingAccountName)")

# Create $20 budget with alerts
gcloud billing budgets create \
  --billing-account=${BILLING_ACCOUNT} \
  --display-name="MCP Server Budget - $20 Max" \
  --budget-amount=20USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=75 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Manual Deployment

### Build and Deploy

```bash
# Build Docker image
gcloud builds submit \
  --tag gcr.io/requirements-mcp-server/mcp-server \
  --timeout=20m

# Deploy to Cloud Run
gcloud run deploy mcp-server \
  --image gcr.io/requirements-mcp-server/mcp-server \
  --platform managed \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 5 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --update-secrets=NOTION_API_KEY=notion-api-key:latest,NOTION_DATABASE_ID=notion-database-id:latest \
  --quiet
```

### Configure Authentication

```bash
# Allow only Google Workspace domain
gcloud run services add-iam-policy-binding mcp-server \
  --region=us-central1 \
  --member="domain:you-source.com" \
  --role="roles/run.invoker"
```

### Build Vector Index

```bash
# Trigger index rebuild
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/rebuild-index
```

## Automated Deployment (GitHub Actions)

### Setup GitHub Secrets

1. Create a service account for GitHub Actions:

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding requirements-mcp-server \
  --member="serviceAccount:github-actions@requirements-mcp-server.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding requirements-mcp-server \
  --member="serviceAccount:github-actions@requirements-mcp-server.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding requirements-mcp-server \
  --member="serviceAccount:github-actions@requirements-mcp-server.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@requirements-mcp-server.iam.gserviceaccount.com
```

2. Add to GitHub Secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Add secret `GCP_SA_KEY` with contents of `github-actions-key.json`
   - Add secrets: `NOTION_API_KEY`, `NOTION_DATABASE_ID`, `NOTION_VIEW_ID`

3. Workflow will auto-deploy on push to main (code changes only)

## Monitoring

### View Logs

```bash
# Recent logs
gcloud run services logs read mcp-server \
  --region us-central1 \
  --limit 50

# Follow logs
gcloud run services logs tail mcp-server \
  --region us-central1
```

### Service Status

```bash
# Get service details
gcloud run services describe mcp-server \
  --region us-central1

# Get service URL
gcloud run services describe mcp-server \
  --region us-central1 \
  --format='value(status.url)'
```

### Cost Monitoring

```bash
# View budget status
gcloud billing budgets list \
  --billing-account=${BILLING_ACCOUNT}

# View current spending
# https://console.cloud.google.com/billing
```

## Testing

### Health Check

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/health
```

### API Endpoints

```bash
# List divisions
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/divisions

# Semantic search
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"query": "user authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

## Troubleshooting

### Service Won't Start

```bash
# Check recent logs for errors
gcloud run services logs read mcp-server \
  --region us-central1 \
  --limit 100 | grep ERROR
```

### Permission Errors

```bash
# Verify service account has required roles
gcloud projects get-iam-policy requirements-mcp-server \
  --flatten="bindings[].members" \
  --filter="bindings.members:${SA_EMAIL}"
```

### Secrets Not Loading

```bash
# List secrets
gcloud secrets list

# Verify secret access
gcloud secrets versions access latest --secret="notion-api-key"
```

### High Costs

1. Check Cloud Run metrics for unexpected scaling
2. Verify budget alerts are configured
3. Review Vertex AI API usage
4. Consider reducing max instances or memory

## Maintenance

### Update Dependencies

1. Update `requirements.txt`
2. Commit and push (triggers auto-deployment)
3. Monitor logs for any errors

### Rebuild Vector Index

Run after major guide changes:

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://mcp-server-375955300575.us-central1.run.app/rebuild-index
```

### Scale Configuration

```bash
# Update instance limits
gcloud run services update mcp-server \
  --region us-central1 \
  --max-instances 10  # Adjust as needed
```

## Security Best Practices

- ✅ Secrets stored in Secret Manager
- ✅ Domain-based authentication (you-source.com)
- ✅ No public access without authentication
- ✅ Service account with minimal permissions
- ✅ Budget alerts configured
- ✅ HTTPS only (enforced by Cloud Run)

## Production Checklist

- [ ] Firestore database created
- [ ] All secrets configured in Secret Manager
- [ ] Service account permissions granted
- [ ] Budget alerts set up ($20 limit)
- [ ] Cloud Run service deployed
- [ ] Domain authentication configured
- [ ] Vector index built (130 guides)
- [ ] API endpoints tested and working
- [ ] GitHub Actions workflows configured
- [ ] Monitoring and logging verified
