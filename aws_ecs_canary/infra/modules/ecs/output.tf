output "http_server_task_definition_arn" {
  value = aws_ecs_task_definition.http_server.arn
}

output "http_server_canary_task_definition_arn" {
  value = aws_ecs_task_definition.http_server_canary.arn
}

output "cluster_arn" {
  value = aws_ecs_cluster.http_server.arn
}
