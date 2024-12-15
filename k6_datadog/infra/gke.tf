resource "google_container_cluster" "chat_app" {
  project                  = var.project
  name                     = "chat-app-cluster"
  location                 = "asia-northeast1-a"
  remove_default_node_pool = true
  initial_node_count       = 1
}


resource "google_container_node_pool" "chat_app_cpu_node_pool" {
  name       = "chat-app-cpu-node-pool"
  location   = "asia-northeast1-a"
  cluster    = google_container_cluster.chat_app.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-standard-4"

    service_account = google_service_account.chat_app_node_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  management {
    auto_repair  = "true"
    auto_upgrade = "true"
  }
}
