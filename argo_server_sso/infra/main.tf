provider "google" {
  project = var.project
  region  = var.region
}

# GKEのservice account
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
resource "google_container_node_pool" "argo_nodes" {
  name     = "argo-node-pool"
  location = "asia-northeast1-a"

  cluster    = google_container_cluster.gke_cluster.name
  project    = var.project
  node_count = 1

  autoscaling {
    max_node_count = 1
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

    tags = ["argo-node-pool"]
  }
}


# Argo Workflows用の外部IP
resource "google_compute_global_address" "argo_workflows_external_ip" {
  name         = "argo-workflows-server-ip"
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
  project      = var.project
}

# DNSゾーン
data "google_dns_managed_zone" "dns_zone" {
  name    = "your-dns-zone"
  project = var.project
}

# Argo Workflows用のDNSレコード
resource "google_dns_record_set" "argo_workflows" {
  project      = var.project
  name         = "argo-workflows.${data.google_dns_managed_zone.dns_zone.dns_name}"
  type         = "A"
  ttl          = 300
  managed_zone = data.google_dns_managed_zone.dns_zone.name
  rrdatas      = [google_compute_global_address.argo_workflows_external_ip.address]
  lifecycle {
    ignore_changes = [rrdatas]
  }
}

# Argo Workflowsのservice account
resource "google_service_account" "argo_workflows_sa" {
  account_id   = "argo-workflows-sa"
  display_name = "argo workflows用のservice account"
}
