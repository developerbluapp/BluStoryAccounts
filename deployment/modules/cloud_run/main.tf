# -----------------------------------
# Deploy Cloud Run service
# -----------------------------------
resource "google_cloud_run_service" "app" {
  name     = var.service_name
  project  = var.project_id
  location = var.region

  template {
    spec {
      service_account_name = var.service_account_email

      containers {
        image = var.image

        # Mount secret
        volume_mounts {
          name       = "service-key"
          mount_path = "/secrets/service-key"
        }

        # Tell the app where credentials are
        env {
          name  = "GOOGLE_APPLICATION_CREDENTIALS"
          value = "/secrets/service-key/latest"
        }
      }

      volumes {
        name = "service-key"
        secret {
          secret_name = var.secret_id
          items {
            key  = "latest"
            path = "latest"
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
  location = google_cloud_run_service.app.location
  project  = var.project_id
  service  = google_cloud_run_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# -----------------------------------
# Output service URL
# -----------------------------------
output "url" {
  value = google_cloud_run_service.app.status[0].url
}
