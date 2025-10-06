variable "project_id" {
  type = string
}

variable "key_file_path" {
  type = string
}

variable "secret_id" {
  type    = string
  default = "blustoryapp-vc-secret"
}

variable "service_account_key_json" {
  type = string
  sensitive = true
}