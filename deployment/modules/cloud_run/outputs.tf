# The full URL of the deployed Cloud Run service
output "cloud_run_url" {
  description = "Public URL of the Cloud Run service"
  value       = google_cloud_run_service.blu_story_app.status[0].url
}

# The name of the Cloud Run service
output "name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_service.blu_story_app.name
}

# The region where the service is deployed
output "region" {
  description = "Region of the Cloud Run service"
  value       = google_cloud_run_service.blu_story_app.location
}

# The latest revision name (useful for debugging or monitoring)
output "latest_revision" {
  description = "Name of the latest Cloud Run revision"
  value       = google_cloud_run_service.blu_story_app.status[0].latest_created_revision_name
}

# The service account used by Cloud Run
output "service_account" {
  description = "Email of the service account used by Cloud Run"
  value       = google_cloud_run_service.blu_story_app.template[0].spec[0].service_account_name
}
