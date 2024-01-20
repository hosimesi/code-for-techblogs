# load balancer用の静的IP
resource "google_compute_global_address" "inference_lb_ip" {
  name         = "inference-lb-ip"
  description  = "inference用のload balancerの静的IP"
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
  project      = var.project
}

# Cloud Run用のサービスアカウント
resource "google_service_account" "inference_cloud_run_service_account" {
  account_id   = "inference-cloud-run"
  display_name = "inference-cloud-run"
  description  = "inference用のcloud run service account"
}

# 推論サーバのCloud Run
resource "google_cloud_run_v2_service" "inference_cloud_run" {
  name        = "inference"
  location    = var.region
  description = "inferenceのcloud run service"
  ingress     = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    containers {
      name  = "inference"
      image = "asia-northeast1-docker.pkg.dev/${var.project}/inference-on-secure-cloud-run/inference:latest"
      ports {
        container_port = 5000
      }
      resources {
        cpu_idle = false
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    service_account = google_service_account.inference_cloud_run_service_account.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

// Cloud Runの未認証呼び出し許可policy
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

// Cloud Runの未認証呼び出し許可を付与
resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_v2_service.inference_cloud_run.location
  project  = var.project
  service  = google_cloud_run_v2_service.inference_cloud_run.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

# cloud run用のservice accountにcloud storageへのアクセス権限付与
resource "google_project_iam_member" "cloud_storage_iam" {
  project = var.project
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.inference_cloud_run_service_account.email}"
}

# Load Balancerのserverless NEG
resource "google_compute_region_network_endpoint_group" "inference_neg" {
  name                  = "inference-neg"
  network_endpoint_type = "SERVERLESS"
  region                = "asia-northeast1"
  # cloud runのserviceを指定
  cloud_run {
    service = google_cloud_run_v2_service.inference_cloud_run.name
  }
}

# Load Balancerのcloud armor policy
resource "google_compute_security_policy" "inference_policy" {
  name        = "inference-policy"
  description = "Load Balancer用のcloud armor policy"
  rule {
    action   = "allow"
    priority = 1000
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        # FIXME: your ip address
        src_ip_ranges = ["your ip address"]
      }
    }
    description = "my home ip address"
  }
  rule {
    action   = "deny(403)"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "default rule"
  }
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable = true
    }
  }
}

# load balancerのbackend service
resource "google_compute_backend_service" "inference_backend_service" {
  name                  = "inference-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL_MANAGED"

  # cloud armor policyを指定
  security_policy = google_compute_security_policy.inference_policy.id

  backend {
    group = google_compute_region_network_endpoint_group.inference_neg.self_link
  }
}

# url map
resource "google_compute_url_map" "inference_url_map" {
  name        = "inference-lb"
  description = "inferenceのload balancer用のlb"

  default_service = google_compute_backend_service.inference_backend_service.id

  path_matcher {
    name            = "inference-apps"
    default_service = google_compute_backend_service.inference_backend_service.id
  }
}

resource "google_compute_target_http_proxy" "inference_target_http_proxy" {
  name    = "predictor-target-http-proxy"
  url_map = google_compute_url_map.inference_url_map.id
}

# フロントエンドの設定(http)
resource "google_compute_global_forwarding_rule" "inference_forwarding_rule_http" {
  name                  = "inference-forwarding-rule-http"
  description           = "load balancerのforwarding rule(http)"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  target                = google_compute_target_http_proxy.inference_target_http_proxy.id
  ip_address            = google_compute_global_address.inference_lb_ip.address
  ip_protocol           = "TCP"
  port_range            = "80"
}
