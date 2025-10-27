# GCP Provider Configuration
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Optional: Backend configuration for storing state
  # Uncomment and configure for production use
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "prompt-firewall/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "prompt-firewall"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "iam.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_dependent_services = false
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "${var.app_name}-docker"
  description   = "Docker repository for ${var.app_name}"
  format        = "DOCKER"
  
  depends_on = [google_project_service.required_apis]
}

# Firestore Database
resource "google_firestore_database" "main" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Secret Manager secrets
resource "google_secret_manager_secret" "encryption_key" {
  secret_id = "${var.app_name}-encryption-key"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  
  depends_on = [google_project_service.required_apis]
}

# Storage bucket for logs (optional)
resource "google_storage_bucket" "logs" {
  name          = "${var.app_name}-logs-${var.project_id}"
  location      = var.region
  force_destroy = false
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Service Account for Cloud Run Backend
resource "google_service_account" "backend_sa" {
  account_id   = "${var.app_name}-backend-sa"
  display_name = "Backend Service Account for Prompt Firewall"
  
  depends_on = [google_project_service.required_apis]
}

# IAM Roles for Backend Service Account
resource "google_project_iam_member" "backend_sa_roles" {
  for_each = toset([
    "roles/datastore.user",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Cloud Run Backend Service
resource "google_cloud_run_service" "backend" {
  name     = "${var.app_name}-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/${var.project_id}/${var.app_name}-docker/backend:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "LOG_LEVEL"
          value = "INFO"
        }
        
        env {
          name  = "ENABLE_METRICS"
          value = "true"
        }
        
        env {
          name  = "ENCRYPTION_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.encryption_key.secret_id
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
          requests = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }
      
      service_account_name = google_service_account.backend_sa.email
      
      container_concurrency = 80
      timeout_seconds       = 300
    }
    
    metadata {
      annotations = {
        "run.googleapis.com/execution-environment" = "gen2"
        "autoscaling.knative.dev/maxScale"         = "10"
        "autoscaling.knative.dev/minScale"         = "1"
        "run.googleapis.com/cpu-throttling"        = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_artifact_registry_repository.docker_repo,
    google_project_iam_member.backend_sa_roles
  ]
}

# Cloud Run Frontend Service
resource "google_cloud_run_service" "frontend" {
  name     = "${var.app_name}-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/${var.project_id}/${var.app_name}-docker/frontend:latest"
        
        ports {
          container_port = 3000
        }
        
        env {
          name  = "NODE_ENV"
          value = "production"
        }
        
        env {
          name  = "NEXT_PUBLIC_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "1Gi"
          }
          requests = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
      
      container_concurrency = 80
      timeout_seconds       = 300
    }
    
    metadata {
      annotations = {
        "run.googleapis.com/execution-environment" = "gen2"
        "autoscaling.knative.dev/maxScale"         = "10"
        "autoscaling.knative.dev/minScale"         = "1"
        "run.googleapis.com/cpu-throttling"        = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_cloud_run_service.backend]
}

# Allow unauthenticated access to Cloud Run services
resource "google_cloud_run_service_iam_member" "backend_public_access" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "frontend_public_access" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "backend_url" {
  description = "Backend API URL"
  value       = google_cloud_run_service.backend.status[0].url
}

output "frontend_url" {
  description = "Frontend URL"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "artifact_registry_url" {
  description = "Artifact Registry URL"
  value       = google_artifact_registry_repository.docker_repo.id
}

