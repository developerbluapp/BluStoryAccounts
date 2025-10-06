# Output the key JSON file content
output "service_account_key_json" {
  value     = google_service_account_key.blu_story_app_sa_key.private_key
  sensitive = true
}