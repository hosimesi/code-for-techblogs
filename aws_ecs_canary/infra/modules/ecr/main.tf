resource "aws_ecr_repository" "http_server" {
  name                 = "http-server/main"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "http_server_canary" {
  name                 = "http-server/canary"
  image_tag_mutability = "MUTABLE"
}
