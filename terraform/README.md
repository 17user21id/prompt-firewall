# Terraform Infrastructure as Code

This directory contains Terraform configuration for deploying Prompt Firewall to Google Cloud Platform.

## Prerequisites

1. Install [Terraform](https://www.terraform.io/downloads) (>= 1.0)
2. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. Authenticate with GCP: `gcloud auth login` and `gcloud auth application-default login`
4. Set your project: `gcloud config set project YOUR_PROJECT_ID`

## Setup

1. **Configure variables:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your project details
   ```

2. **Initialize Terraform:**
   ```bash
   terraform init
   ```

3. **Plan the deployment:**
   ```bash
   terraform plan
   ```

4. **Apply the configuration:**
   ```bash
   terraform apply
   ```

## What It Creates

- **Artifact Registry**: Docker image repository
- **Firestore Database**: Native Firestore database for logs and data
- **Secret Manager**: For encryption keys and sensitive data
- **Cloud Run Services**: Backend API and frontend web app
- **IAM Roles**: Service accounts with appropriate permissions
- **Storage Bucket**: For log storage (optional)

## Costs

Estimated monthly costs for typical usage:
- Cloud Run: ~$10-20 (based on traffic)
- Firestore: ~$5-10 (based on operations)
- Artifact Registry: ~$1-2 (storage)
- Secret Manager: ~$1-2
- Storage: ~$1-2

**Total: ~$20-40/month** for typical usage

## Destroying Resources

To destroy all resources:
```bash
terraform destroy
```

## State Management

For production use, configure a remote backend in `main.tf` to store Terraform state in Google Cloud Storage.

