resource "aws_ecs_cluster" "http_server" {
  name = "http-server"
}

resource "aws_ecs_task_definition" "http_server" {
  family                   = "http-server"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/http_server.json", {
    http_server_ecr_uri = "${var.http_server_ecr_uri}",
  })
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}

resource "aws_ecs_task_definition" "http_server_canary" {
  family                   = "http-server-canary"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/http_server_canary.json", {
    http_server_canary_ecr_uri = "${var.http_server_canary_ecr_uri}",
  })
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}

resource "aws_ecs_service" "http_server" {
  name                               = "http-server-service"
  cluster                            = aws_ecs_cluster.http_server.name
  task_definition                    = aws_ecs_task_definition.http_server.arn
  desired_count                      = 1
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  launch_type                        = "FARGATE"
  network_configuration {
    security_groups = [var.http_server_security_group]
    subnets         = var.private_subnets
  }

  load_balancer {
    target_group_arn = var.http_server_target_group_arn
    container_name   = "http-server"
    container_port   = 8080
  }
}

resource "aws_ecs_service" "http_server_canary" {
  name                               = "http-server-canary-service"
  cluster                            = aws_ecs_cluster.http_server.name
  task_definition                    = aws_ecs_task_definition.http_server_canary.arn
  desired_count                      = 1
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  launch_type                        = "FARGATE"
  network_configuration {
    security_groups = [var.http_server_security_group]
    subnets         = var.private_subnets
  }

  load_balancer {
    target_group_arn = var.http_server_canary_target_group_arn
    container_name   = "http-server-canary"
    container_port   = 8080
  }
}
