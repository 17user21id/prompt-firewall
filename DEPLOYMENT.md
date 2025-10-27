# Prompt Firewall - Deployment Guide

Complete guide for deploying the Prompt Firewall to Google Cloud Platform using Infrastructure as Code and CI/CD.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [Manual Deployment](#manual-deployment)
6. [CI/CD Setup](#cicd-setup)
7. [Monitoring](#monitoring)
8. [Cost Estimation](#cost-estimation)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

## Overview

This deployment setup provides:
- **Infrastructure as Code** using Terraform
- **CI/CD Pipeline** via GitHub Actions and Cloud Build
- **Serverless Deployment** on GCP Cloud Run
- **Monitoring** with Cloud Monitoring and Prometheus
- **Automated Scaling** and load balancing
- **Secure Secrets Management** via Secret Manager

## Prerequisites

Before deploying, ensure you have:

1. **GCP Account** with billing enabled
2. **GitHub Account** with repository access
3. **Installed Tools**:
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (gcloud)
   - [Terraform](https://www.terraform.io/downloads) (>= 1.0)
   - [Docker](https://www.docker.com/get-started)
   - [Node.js](https://nodejs.org/) (>= 18)
   - [Python](https://www.python.org/) (>= 3.11)

4. **Authentication**:
   ```bash
   # Authenticate with Google Cloud
   gcloud auth login
   gcloud auth application-default login
   
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable \
     cloudresourcemanager.googleapis.com \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     artifactregistry.googleapis.com \
     firestore.googleapis.com \
     secretmanager.googleapis.com \
     monitoring.googleapis.com \
     logging.googleapis.com
   ```

## Architecture

```
┌─────────────────┐
│   End Users     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Cloud Run Frontend             │
│      (Next.js Application)          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Cloud Run Backend              │
│      (FastAPI Application)         │
└────────┬────────────────────────────┘
         │
         ├──────────────────┬──────────────┐
         │                  │              │
         ▼                  ▼              ▼
┌─────────────┐    ┌──────────────┐  ┌─────────────┐
│  Firestore  │    │   Secret     │  │ Monitoring  │
│  Database   │    │   Manager    │  │ & Logging   │
└─────────────┘    └──────────────┘  └─────────────┘
```

### Components

- **Cloud Run**: Serverless container platform (auto-scaling, pay-per-use)
- **Firestore**: NoSQL database for logs and configurations
- **Artifact Registry**: Docker image storage
- **Secret Manager**: Secure credential storage
- **Cloud Monitoring**: Metrics and observability
- **Cloud Logging**: Centralized log management

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/your-username/prompt-firewall.git
cd prompt-firewall
```

### 2. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project details
```

### 3. Initialize Terraform

```bash
terraform init
terraform plan
terraform apply
```

### 4. Build Docker Images

```bash
# Build backend
cd ../backend
docker build -t gcr.io/YOUR_PROJECT_ID/prompt-firewall-backend:latest .

# Build frontend
cd ../frontend
docker build -t gcr.io/YOUR_PROJECT_ID/prompt-firewall-frontend:latest .
```

### 5. Push Images to Registry

```bash
# Authenticate Docker
gcloud auth configure-docker

# Push backend
docker push gcr.io/YOUR_PROJECT_ID/prompt-firewall-backend:latest

# Push frontend
docker push gcr.io/YOUR_PROJECT_ID/prompt-firewall-frontend:latest
```

### 6. Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy prompt-firewall-backend \
  --image gcr.io/YOUR_PROJECT_ID/prompt-firewall-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe prompt-firewall-backend \
  --region us-central1 --format 'value(status.url)')

# Deploy frontend
gcloud run deploy prompt-firewall-frontend \
  --image gcr.io/YOUR_PROJECT_ID/prompt-firewall-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"
```

## Manual Deployment

### Option 1: Using Cloud Build

```bash
# Submit build using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml \
  --substitutions _REPO_NAME=prompt-firewall-docker
```

### Option 2: Using GitHub Actions

1. Fork the repository
2. Add GitHub Secrets:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Service account JSON key
3. Push to main branch - deployment happens automatically

### Option 3: Using Terraform

```bash
cd terraform
terraform apply -auto-approve
```

## CI/CD Setup

### GitHub Actions

The workflow (`.github/workflows/deploy.yml`) automatically:
1. Runs tests on push/PR
2. Builds Docker images
3. Pushes to Artifact Registry
4. Deploys to Cloud Run
5. Updates environment variables

### Setup GitHub Secrets

1. Go to Repository → Settings → Secrets
2. Add these secrets:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Service account key (JSON)

### Create Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Add key.json content to GitHub secret GCP_SA_KEY
```

### Trigger Deployment

Deployments happen automatically on:
- Push to `main` branch
- Manual workflow trigger

## Monitoring

### Cloud Monitoring

Access dashboards at:
- https://console.cloud.google.com/monitoring

Key metrics:
- Request count
- Request latency
- Error rate
- PII detections
- Prompt injection attempts

### Prometheus Metrics

Access metrics endpoint:
```bash
curl https://YOUR-BACKEND-URL/metrics
```

Available metrics:
- `firewall_requests_total`
- `firewall_request_duration_seconds`
- `firewall_pii_detections_total`
- `firewall_injection_detections_total`
- `firewall_active_connections`

### Logging

View logs:
```bash
# View backend logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# View error logs
gcloud logging read "severity>=ERROR" --limit 50

# Tail logs
gcloud logging tail "resource.type=cloud_run_revision"
```

## Cost Estimation

### Monthly Costs (Estimated)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 2M requests, 1M requests | $10-30 |
| Firestore | 100K reads/writes/day | $5-15 |
| Artifact Registry | 5 GB storage | $1-2 |
| Secret Manager | 10 secrets | $1 |
| Cloud Storage | Log storage (optional) | $1-2 |
| Cloud Monitoring | Standard tier | Free |
| **Total** | | **$20-50/month** |

### Cost Optimization

1. **Use Cloud Run min-instances=1** only for production
2. **Enable Firestore daily limits** to prevent overage
3. **Archive old logs** to cheaper storage
4. **Monitor usage** with billing alerts

## Security

### Best Practices Implemented

1. **Secrets Management**:
   - Encryption keys in Secret Manager
   - No secrets in code or environment variables
   - Rotation policies

2. **IAM**:
   - Least privilege access
   - Service accounts for Cloud Run
   - No over-broad permissions

3. **Network**:
   - VPC connectors (optional)
   - Private IP (optional)
   - HTTPS only

4. **Application**:
   - Input validation
   - Rate limiting
   - Audit logging
   - PII detection and redaction

### Security Hardening

```bash
# Enable VPC connector (recommended for production)
gcloud compute networks vpc-access connectors create prompt-firewall-connector \
  --region=us-central1 \
  --subnet=default \
  --min-instances=2 \
  --max-instances=3

# Update Cloud Run to use VPC connector
gcloud run services update prompt-firewall-backend \
  --vpc-connector=prompt-firewall-connector \
  --region=us-central1
```

## Troubleshooting

### Common Issues

#### 1. Build Failures

```bash
# Check build logs
gcloud builds log LAST_BUILD_ID

# Rebuild with verbose output
gcloud builds submit --config cloudbuild.yaml --verbosity=debug
```

#### 2. Deployment Failures

```bash
# Check service status
gcloud run services describe prompt-firewall-backend \
  --region us-central1

# View recent revisions
gcloud run revisions list --service prompt-firewall-backend

# Rollback to previous revision
gcloud run services update-traffic prompt-firewall-backend \
  --to-revisions PREVIOUS_REVISION=100
```

#### 3. Connection Issues

```bash
# Test backend health
curl https://YOUR-BACKEND-URL/health

# Test frontend
curl https://YOUR-FRONTEND-URL/

# Check CORS configuration
curl -H "Origin: https://YOUR-FRONTEND-URL" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS \
  https://YOUR-BACKEND-URL/v1/query
```

#### 4. Firestore Connection

```bash
# Test Firestore connection
gcloud firestore databases list

# Check Firestore rules
gcloud firestore security-rules list
```

### Debugging Commands

```bash
# View running containers
gcloud run services list

# Get service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=prompt-firewall-backend" --limit 100

# SSH into Cloud Run (if applicable)
gcloud beta run services proxy prompt-firewall-backend --port=8080

# Test locally with Cloud Run emulator
gcloud beta emulators cloud-run start
```

### Health Checks

```bash
# Backend health
curl https://YOUR-BACKEND-URL/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-01-27T10:00:00",
  "version": "1.0.0",
  "services": {
    "firestore": "healthy",
    "detector": "healthy",
    "rules_engine": "healthy"
  }
}

# Metrics endpoint
curl https://YOUR-BACKEND-URL/metrics
```

## Production Deployment Checklist

- [ ] Set up GCP project with billing enabled
- [ ] Create and configure Terraform state backend
- [ ] Deploy infrastructure with Terraform
- [ ] Configure GitHub Actions secrets
- [ ] Set up monitoring dashboards
- [ ] Configure alerting policies
- [ ] Set up backup for Firestore
- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Configure custom domain
- [ ] Set up SSL certificates
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set budget alerts
- [ ] Enable audit logging

## Support

For issues and questions:
- **Issues**: GitHub Issues
- **Documentation**: This file and `/docs`
- **Logs**: GCP Console → Cloud Logging

---

**Last Updated**: January 2025
**Version**: 1.0.0

