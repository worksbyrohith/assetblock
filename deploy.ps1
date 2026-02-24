#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Deploys AssetBlock to Google Cloud Run in one shot.
  Requires: gcloud CLI installed and authenticated.

.USAGE
  cd c:\Users\Rohith\Downloads\assetblock
  .\deploy.ps1
#>

# ── CONFIG ────────────────────────────────────────────────────────────────────
$PROJECT_ID   = "assetblock-3df65"
$REGION       = "us-central1"
$API_IMAGE    = "gcr.io/$PROJECT_ID/assetblock-api"
$CLIENT_IMAGE = "gcr.io/$PROJECT_ID/assetblock-client"
$ADMIN_IMAGE  = "gcr.io/$PROJECT_ID/assetblock-admin"

# ── ENV VARS passed to Cloud Run (no .env file in containers) ─────────────────
$FIREBASE_WEB_API_KEY          = "AIzaSyCdF2-vOL2oJPOfe-mVKaJeimXtSqH6BPc"
$FIREBASE_AUTH_DOMAIN          = "assetblock-3df65.firebaseapp.com"
$FIREBASE_PROJECT_ID           = "assetblock-3df65"
$FIREBASE_STORAGE_BUCKET       = "assetblock-3df65.appspot.com"
$FIREBASE_MESSAGING_SENDER_ID  = ""
$FIREBASE_APP_ID               = ""
$POSTGRE_USER                  = "postgres"
$POSTGRE_PASSWORD              = "admin123"
$POSTGRE_PORT                  = "5432"
$POSTGRE_DB                    = "assetblock"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  AssetBlock — Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ── STEP 1: Set project ───────────────────────────────────────────────────────
Write-Host "[1/9] Setting GCloud project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# ── STEP 2: Enable required APIs ─────────────────────────────────────────────
Write-Host "[2/9] Enabling Cloud Run & Container Registry APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com containerregistry.googleapis.com sqladmin.googleapis.com

# ── STEP 3: Configure Docker auth ────────────────────────────────────────────
Write-Host "[3/9] Configuring Docker auth for GCR..." -ForegroundColor Yellow
gcloud auth configure-docker --quiet

# ── STEP 4: Build & push API ──────────────────────────────────────────────────
Write-Host "[4/9] Building FastAPI backend image..." -ForegroundColor Yellow
docker build -f Dockerfile.api -t $API_IMAGE .
docker push $API_IMAGE

# ── STEP 5: Deploy API to Cloud Run ──────────────────────────────────────────
Write-Host "[5/9] Deploying API to Cloud Run..." -ForegroundColor Yellow
$API_URL = gcloud run deploy assetblock-api `
  --image $API_IMAGE `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8000 `
  --set-env-vars "FIREBASE_WEB_API_KEY=$FIREBASE_WEB_API_KEY,FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN,FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID,FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET,POSTGRE_USER=$POSTGRE_USER,POSTGRE_PASSWORD=$POSTGRE_PASSWORD,POSTGRE_HOST=`$POSTGRE_HOST,POSTGRE_PORT=$POSTGRE_PORT,POSTGRE_DB=$POSTGRE_DB" `
  --format "value(status.url)" `
  --quiet 2>&1 | Select-Object -Last 1

# Get the actual API URL
$API_URL = gcloud run services describe assetblock-api --platform managed --region $REGION --format "value(status.url)"
Write-Host "  ✓ API deployed at: $API_URL" -ForegroundColor Green

# ── STEP 6: Build & push Client ───────────────────────────────────────────────
Write-Host "[6/9] Building Client UI image..." -ForegroundColor Yellow
docker build -f Dockerfile.client -t $CLIENT_IMAGE .
docker push $CLIENT_IMAGE

# ── STEP 7: Deploy Client to Cloud Run ────────────────────────────────────────
Write-Host "[7/9] Deploying Client UI to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy assetblock-client `
  --image $CLIENT_IMAGE `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8501 `
  --set-env-vars "FIREBASE_WEB_API_KEY=$FIREBASE_WEB_API_KEY,FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN,FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID,FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET,API_BASE_URL=$API_URL" `
  --quiet

$CLIENT_URL = gcloud run services describe assetblock-client --platform managed --region $REGION --format "value(status.url)"
Write-Host "  ✓ Client deployed at: $CLIENT_URL" -ForegroundColor Green

# ── STEP 8: Build & push Admin ────────────────────────────────────────────────
Write-Host "[8/9] Building Admin UI image..." -ForegroundColor Yellow
docker build -f Dockerfile.admin -t $ADMIN_IMAGE .
docker push $ADMIN_IMAGE

# ── STEP 9: Deploy Admin to Cloud Run ─────────────────────────────────────────
Write-Host "[9/9] Deploying Admin UI to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy assetblock-admin `
  --image $ADMIN_IMAGE `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8502 `
  --set-env-vars "FIREBASE_WEB_API_KEY=$FIREBASE_WEB_API_KEY,FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN,FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID,FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET,API_BASE_URL=$API_URL" `
  --quiet

$ADMIN_URL = gcloud run services describe assetblock-admin --platform managed --region $REGION --format "value(status.url)"
Write-Host "  ✓ Admin deployed at: $ADMIN_URL" -ForegroundColor Green

# ── DONE ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  API   : $API_URL/docs" -ForegroundColor Cyan
Write-Host "  Client: $CLIENT_URL" -ForegroundColor Cyan
Write-Host "  Admin : $ADMIN_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "  NOTE: Set POSTGRE_HOST in Cloud Run to your" -ForegroundColor Yellow
Write-Host "  cloud database host (see walkthrough for Supabase setup)" -ForegroundColor Yellow
Write-Host ""
