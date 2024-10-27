output "http_server_ecr_uri" {
  value = aws_ecr_repository.http_server.repository_url
}

output "http_server_canary_ecr_uri" {
  value = aws_ecr_repository.http_server_canary.repository_url
}
