#!/bin/bash

# Prompt Firewall Deployment Script
# Run this script to deploy both backend and frontend

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Step 1: Build backend
echo ""
echo "📦 Step 1: Building backend..."
cd backend
docker build -t us-central1-docker.pkg.dev/prompt-firewall-mvp/prompt-firewall-docker/backend:latest .

# Step 2: Push backend
echo ""
echo "📤 Step 2: Pushing backend image..."
docker push us-central1-docker.pkg.dev/prompt-firewall-mvp/prompt-firewall-docker/backend:latest

# Step 3: Build frontend
echo ""
echo "🎨 Step 3: Building frontend..."
cd ../frontend
docker build -t us-central1-docker.pkg.dev/prompt-firewall-mvp/prompt-firewall-docker/frontend:latest .

# Step 4: Push frontend
echo ""
echo "📤 Step 4: Pushing frontend image..."
docker push us-central1-docker.pkg.dev/prompt-firewall-mvp/prompt-firewall-docker/frontend:latest

# Step 5: Deploy backend
echo ""
echo "☁️  Step 5: Deploying backend to Cloud Run..."
cd ..
gcloud run deploy prompt-firewall-backend \
  --image us-central1-docker.pkg.dev/prompt-firewall-mvp/prompt-firewall-docker/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8000 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=prompt-firewall-mvp,LOG_LEVEL=INFO"

# Step 6: Get backend URL
BACKEND_URL=$(gcloud run services describe prompt-firewall-backend --region us-central1 --format 'value(status.url)')
echo ""
echo "✅ Backend deployed at: $BACKEND_URL"

# Step 7: Deploy frontend
echo ""
echo "☁️  Step 7: Deploying frontend to Cloud Run..."
gcloud run deploy prompt-firewall-frontend \
  --image us-central1-docker.pkg.dev/prompt-firewall-mvp/prompt-firewall-docker/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"

# Step 8: Get frontend URL
FRONTEND_URL=$(gcloud run services describe prompt-firewall-frontend --region us-central1 --format 'value(status.url)')
echo ""
echo "✅ Frontend deployed at: $FRONTEND_URL"

# Summary
echo ""
echo "=============================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "Your Public URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Backend API:  $BACKEND_URL"
echo "🌐 Frontend UI:  $FRONTEND_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

