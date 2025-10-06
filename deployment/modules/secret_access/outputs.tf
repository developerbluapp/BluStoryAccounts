# -----------------------------------
# Outputs
# -----------------------------------
output "cloud_run_sa_email" {
  value = google_service_account.cloud_run_sa.email
}

output "secret_id" {
  value = google_secret_manager_secret.service_account_key.secret_id
}
