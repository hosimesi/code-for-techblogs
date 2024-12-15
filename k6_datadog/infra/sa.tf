
resource "google_service_account" "chat_app_node_sa" {
  account_id   = "chat-app-node-sa"
  display_name = "chat-app-node-sa"
}


resource "google_service_account" "chat_app_sa" {
  account_id   = "chat-app-sa"
  display_name = "chat-app-sa"
}

resource "google_service_account_iam_binding" "app" {
  service_account_id = google_service_account.chat_app_sa.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project}.svc.id.goog[default/chat-app-serviceaccount]"
  ]
}

resource "google_project_iam_member" "artifact_registry_iam" {
  project = var.project
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.chat_app_node_sa.email}"
}

resource "google_project_iam_member" "service_account_token_creator_iam" {
  project = var.project
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.chat_app_sa.email}"
}
