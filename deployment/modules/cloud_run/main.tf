# -----------------------------------
# Deploy Cloud Run service
# -----------------------------------
resource "google_cloud_run_service" "blu_story_app" {
  name     = var.service_name
  project  = var.project_id
  location = var.region

  template {
    spec {
      # Service account running Cloud Run
      service_account_name = var.service_account_email

      containers {
        image = var.image

        # Mount the Secret Manager secret
        volume_mounts {
          name       = var.secret_id
          mount_path = "/secrets/service-key"
        }

        # Tell the app where credentials are
        env {
          name  = "GOOGLE_APPLICATION_CREDENTIALS"
          value = "/secrets/service-key/service_account.json"
        }
      }

      # Define the volume with the secret
      volumes {
        name = var.secret_id
        secret {
          secret_name = var.secret_id
          items {
            key  = "latest"     # The key name in Secret Manager
            path = "service_account.json"     # File name inside container
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# -----------------------------------
# Allow public access (optional)
# -----------------------------------
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_service.blu_story_app.location
  project  = var.project_id
  service  = google_cloud_run_service.blu_story_app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}