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

# ----------------------------
# 1. Service Account + Secret module
# ----------------------------
module "service_accounts" {
  source          = "./modules/service_accounts"
  project_id      = var.project_id
  key_file_path   =  var.key_file_path
  secret_id       =  var.secret_id
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
  service_account_email = module.service_accounts.cloud_run_sa_email
  secret_id             = module.service_accounts.secret_id
}

