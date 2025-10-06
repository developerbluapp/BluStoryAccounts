
# -----------------------------------
# Create Secret Manager secret + version
# -----------------------------------
resource "google_secret_manager_secret" "service_account_key" {
  secret_id = var.secret_id
  replication {
     auto {}
  }
}

resource "google_secret_manager_secret_version" "service_account_key_version" {
  secret      = google_secret_manager_secret.service_account_key.id
  secret_data = file(var.key_file_path)
}

# -----------------------------------
# Create Cloud Run service account
# -----------------------------------
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}

# -----------------------------------
# Allow service account access to secret
# -----------------------------------
resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id = google_secret_manager_secret.service_account_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Optional example: Storage access
resource "google_project_iam_member" "storage_access" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

