provider "google" {
  project = var.project
  region  = var.region
}

# argo workflowsのartifact registry
resource "google_artifact_registry_repository" "argo_workflows_artifact_registry_repository" {
  location      = var.region
  repository_id = "argo-workflows"
  description   = "argo workflowsのartifact registry"
  format        = "DOCKER"
}

# argo workflows用のservice account(強めの権限与える)
resource "google_service_account" "argo_workflows_sa" {
  account_id   = "argo-workflows-sa"
  display_name = "argo workflows用のservice account"
}

# argo workflowsのservice accountにstorageのアクセス権限を付与
resource "google_project_iam_member" "workflows_storage_iam" {
  project = var.project
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.argo_workflows_sa.email}"
}

# argo workflowsのservice accountにartifact registryのアクセス権限を付与
resource "google_project_iam_member" "workflows_artifact_registry_iam" {
  project = var.project
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.argo_workflows_sa.email}"
}

# argo workflowsのservice accountにpubsubのアクセス権限を付与
resource "google_project_iam_member" "workflows_pubsub_publisher_iam" {
  project = var.project
  role    = "roles/pubsub.admin"
  member  = "serviceAccount:${google_service_account.argo_workflows_sa.email}"
}

# ========================================
# argo events用のservice account
resource "google_service_account" "argo_events_sa" {
  account_id   = "argo-events-sa"
  display_name = "argo events用のservice account"
}

# argo eventsのservice accountにpubsubのアクセス権限を付与
resource "google_project_iam_member" "events_pubsub_subscriber_iam" {
  project = var.project
  role    = "roles/pubsub.admin"
  member  = "serviceAccount:${google_service_account.argo_events_sa.email}"
}


# ========================================
# workflow用のbucket
resource "google_storage_bucket" "argo_workflows_bucket" {
  name                     = "argo-workflows-bucket"
  force_destroy            = false
  storage_class            = "STANDARD"
  location                 = "ASIA-NORTHEAST1"
  project                  = var.project
  public_access_prevention = "inherited"

  cors {
    max_age_seconds = 3600
    method          = ["GET"]
    origin          = ["*"]
    response_header = ["Content-Type", "Access-Control-Allow-Origin"]
  }

  versioning {
    enabled = true
  }
}


# ========================================
# train用のbucket
resource "google_storage_bucket" "train_workflows_bucket" {
  name                     = "train-workflows-bucket"
  force_destroy            = false
  storage_class            = "STANDARD"
  location                 = "ASIA-NORTHEAST1"
  project                  = var.project
  public_access_prevention = "inherited"

  cors {
    max_age_seconds = 3600
    method          = ["GET"]
    origin          = ["*"]
    response_header = ["Content-Type", "Access-Control-Allow-Origin"]
  }

  versioning {
    enabled = true
  }
}

# ========================================
# argo events用のpubsub topic
# workflowをkickする用のpubsub topic
resource "google_pubsub_topic" "argo_workflows_topic" {
  name    = "argo-workflows-topic"
  project = var.project
}

# workflowをkickする用のpubsub subscription
resource "google_pubsub_subscription" "argo_workflows_topic_subscription" {
  depends_on = [
    google_pubsub_topic.argo_workflows_topic
  ]
  name                       = "argo-workflows-topic-sub"
  project                    = var.project
  topic                      = google_pubsub_topic.argo_workflows_topic.name
  ack_deadline_seconds       = 20
  message_retention_duration = "3600s"
  retain_acked_messages      = true
  expiration_policy {
    ttl = "2678400s"
  }
}
