#!/bin/bash

# Prompt Firewall Deployment Script
# Run this script to deploy both backend and frontend
# Fixed for Apple Silicon (M1/M2) -> Cloud Run (x86_64) compatibility

set -e  # Exit on error

echo "Starting deployment..."

# === CONFIG ===
PROJECT_ID="prompt-firewall-mvp"
REGION="us-central1"
BACKEND_IMAGE="us-central1-docker.pkg.dev/$PROJECT_ID/prompt-firewall-docker/backend:latest"
FRONTEND_IMAGE="us-central1-docker.pkg.dev/$PROJECT_ID/prompt-firewall-docker/frontend:latest"
BACKEND_SERVICE="prompt-firewall-backend"
FRONTEND_SERVICE="prompt-firewall-frontend"
PLATFORM="linux/amd64"  # Critical: Match Cloud Run architecture

# Step 1: Build & Push Backend
echo ""
echo "Step 1: Building backend ($PLATFORM)..."
cd backend
docker build --platform $PLATFORM -t $BACKEND_IMAGE .

echo ""
echo "Step 2: Pushing backend image..."
docker push $BACKEND_IMAGE

# Step 3: Build & Push Frontend
echo ""
echo "Step 3: Building frontend ($PLATFORM)..."
cd ../frontend
docker build --platform $PLATFORM -t $FRONTEND_IMAGE .

echo ""
echo "Step 4: Pushing frontend image..."
docker push $FRONTEND_IMAGE

# Step 5: Deploy Backend
echo ""
echo "Step 5: Deploying backend to Cloud Run..."
cd ..
gcloud run deploy $BACKEND_SERVICE \
  --image $BACKEND_IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8000 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,LOG_LEVEL=INFO" \
  --quiet

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
echo ""
echo "Backend deployed at: $BACKEND_URL"

# Step 6: Deploy Frontend with Backend URL
echo ""
echo "Step 6: Deploying frontend to Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE \
  --image $FRONTEND_IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL" \
  --quiet

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --format 'value(status.url)')
echo ""
echo "Frontend deployed at: $FRONTEND_URL"

# Summary
echo ""
echo "=============================================="
echo "DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "Your Public URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend API:  $BACKEND_URL"
echo "Frontend UI:  $FRONTEND_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""