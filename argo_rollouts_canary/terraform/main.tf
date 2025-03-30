provider "google" {
  project = var.project
  region  = var.region
}

# GKE用のservice account
resource "google_service_account" "gke_sa" {
  account_id   = "gke-sa"
  display_name = "gke用のservice account"
}

# GKE Cluster
resource "google_container_cluster" "gke_cluster" {
  name                = "gke-cluster"
  location            = "asia-northeast1-a"
  project             = var.project
  deletion_protection = false

  remove_default_node_pool = true
  initial_node_count       = 1

}

# GKE Node Pool
resource "google_container_node_pool" "argo_rollouts_node_pool" {
  name     = "argo-rollouts-node-pool"
  location = "asia-northeast1-a"

  cluster    = google_container_cluster.gke_cluster.name
  project    = var.project
  node_count = 1

  autoscaling {
    max_node_count = 5
    min_node_count = 1
  }

  node_config {
    preemptible  = true
    machine_type = "e2-medium"

    service_account = google_service_account.gke_sa.email

    metadata = {
      disable-legacy-endpoints = "true"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    labels = {
      preemptible = "true"
    }

    tags = ["argo-rollouts-node-pool"]
  }
}

# Argo Rollouts用のArtifact Registry
resource "google_artifact_registry_repository" "argo_rollouts_repository" {
  location      = "asia-northeast1"
  repository_id = "argo-rollouts"
  description   = "Argo Rollouts"
  format        = "DOCKER"
}


# nodepool
resource "google_project_iam_member" "gke_node_service_account" {
  project = var.project
  role    = "roles/container.nodeServiceAccount"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}


resource "google_compute_subnetwork" "argo_rollouts_subnet" {
  name          = "argo-rollouts-subnet"
  ip_cidr_range = "10.1.1.0/24"
  region        = var.region
  network       = "default"

  purpose = "REGIONAL_MANAGED_PROXY"
  role    = "ACTIVE"
}
