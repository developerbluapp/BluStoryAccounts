terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "service_accounts" {
  source     = "./modules/service_accounts"
  project_id = var.project_id
}

# ----------------------------
# 1. Service Account + Secret module
# ----------------------------
module "secret_access" {
  source          = "./modules/secret_access"
  project_id      = var.project_id
  key_file_path   =  var.key_file_path
  service_account_key_json = module.service_accounts.service_account_key_json
  secret_id       =  var.secret_id
  depends_on     = [module.service_accounts]
}

# ----------------------------
# 2. Cloud Run module
# ----------------------------
module "cloud_run" {
  source                = "./modules/cloud_run"
  project_id            = var.project_id
  service_name          = var.service_name
  region                = var.region
  image                 = var.image
  service_account_email = module.secret_access.blustory_cloud_run_sa_email
  secret_id             = module.secret_access.secret_id
  depends_on           = [module.secret_access, module.service_accounts]
}

