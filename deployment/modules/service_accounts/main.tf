# Create the service account
resource "google_service_account" "blu_story_app_sa" {
    project      = var.project_id
  account_id   = "blu-story-app-storage-sa"
  display_name = "My Storage Service Account"
}

# Grant Storage Admin role to the service account
resource "google_project_iam_member" "blu_story_app_sa_role" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.blu_story_app_sa.email}"
}

# Create a key for the service account (JSON)
resource "google_service_account_key" "blu_story_app_sa_key" {
  service_account_id = google_service_account.blu_story_app_sa.name
  key_algorithm      = "KEY_ALG_RSA_2048"
  private_key_type   = "TYPE_GOOGLE_CREDENTIALS_FILE"
}
