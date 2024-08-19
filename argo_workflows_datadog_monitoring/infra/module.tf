resource "google_service_account" "argo_monitoring" {
  account_id   = "argo-monitoring"
  display_name = "argo-monitoring"
}

resource "google_container_cluster" "argo_monitroing" {
  project                  = var.project
  name                     = "argo-monitoring-cluster"
  location                 = "asia-northeast1-a"
  remove_default_node_pool = true
  initial_node_count       = 1
}


resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "argo-monitoring-node-pool"
  location   = "asia-northeast1-a"
  cluster    = google_container_cluster.argo_monitroing.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-medium"

    service_account = google_service_account.argo_monitoring.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}


