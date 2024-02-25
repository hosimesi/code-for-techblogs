provider "google" {
  project = var.project
  region  = var.region
}

resource "google_service_account" "github_actions_service_account" {
  account_id   = "github-actions-sa"
  display_name = "github actions service account"
}

resource "google_service_account" "sample_cloud_run_service_account" {
  account_id   = "sample-cloud-run-sa"
  display_name = "sample cloud run service account"
}

resource "google_artifact_registry_repository" "sample_artifact_registry_repository" {
  location      = var.region
  repository_id = "sample-artifact-registry-repository"
  description   = "sample artifact registry repository"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "sample_cloud_run" {
  name        = "sample-cloud-run"
  location    = var.region
  description = "sample cloud run service"
  ingress     = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      name = "sample-cloud-run"
      # FIXME: Replace with your artifact registry repository
      image = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.sample_artifact_registry_repository.repository_id}/sample-image:latest"
      ports {
        container_port = 80
      }
      resources {
        cpu_idle = true
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    service_account = google_service_account.sample_cloud_run_service_account.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_v2_service.sample_cloud_run.location
  project  = var.project
  service  = google_cloud_run_v2_service.sample_cloud_run.name

  policy_data = data.google_iam_policy.noauth.policy_data
}


# github actions用
resource "google_iam_workload_identity_pool" "sample_gh_act_pool" {
  workload_identity_pool_id = "sample-gh-act-pool"
  display_name              = "sample-gh-act-pool"
  description               = "Pool for GitHub Actions"
  disabled                  = false
}

resource "google_iam_workload_identity_pool_provider" "sample_gh_act_provider" {
  workload_identity_pool_provider_id = "sample-gh-act-provider"
  workload_identity_pool_id          = google_iam_workload_identity_pool.sample_gh_act_pool.workload_identity_pool_id
  display_name                       = "sample-gh-act-provider"
  description                        = "Provider for GitHub Actions"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}


resource "google_project_iam_member" "artifact_registry_writer" {
  project = var.project
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}


resource "google_project_iam_member" "service_account_user" {
  project = var.project
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}


resource "google_project_iam_member" "admin" {
  project = var.project
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}

resource "google_project_iam_member" "workload_identity_user" {
  project = var.project
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}

resource "google_service_account_iam_binding" "workload_identity_user" {
  service_account_id = google_service_account.github_actions_service_account.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    # FIXME: Replace with your workload identity pool name
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.sample_gh_act_pool.name}/attribute.repository/hosimesi/code-for-techblogs"
  ]
}
