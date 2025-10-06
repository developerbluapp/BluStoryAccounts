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



