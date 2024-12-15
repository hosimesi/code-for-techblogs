resource "google_artifact_registry_repository" "chat_app" {
  location      = var.region
  repository_id = "chat-app"
  description   = "chat-app用のArtifact Registry"
  format        = "DOCKER"
}
