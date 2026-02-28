#!/bin/bash
# ==========================================================
# Google Cloud: Create Full Storage Admin Service Account
# ==========================================================

# --- CONFIGURATION ---
PROJECT_ID="blustoryapp"              # e.g. my-gcp-project
SERVICE_ACCOUNT_NAME="blustory-storage-sa"   # choose a short, unique name
DISPLAY_NAME="Full Storage Admin Service Account"
KEY_FILE_PATH="./service_account.json"  # optional: where to save key file

# --- 1. Set active project ---
echo "🔧 Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# --- 2. Create the service account ---
echo "👤 Creating service account: $SERVICE_ACCOUNT_NAME"
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="$DISPLAY_NAME"

# --- 3. Grant full Cloud Storage Admin role ---
echo "🪣 Granting Storage Admin role to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# --- 4. (Optional) Create and download a key for authentication ---
echo "🔑 Creating service account key file: $KEY_FILE_PATH"
gcloud iam service-accounts keys create "$KEY_FILE_PATH" \
  --iam-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# --- 5. Confirm assignment ---
echo "✅ Verifying IAM roles for service account..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --format="table(bindings.role)"

echo "🎉 All done!"
echo "Service Account: ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Key File: $KEY_FILE_PATH"
