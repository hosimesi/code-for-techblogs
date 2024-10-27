output "http_server_target_group_arn" {
  value = aws_lb_target_group.http_server.arn
}

output "http_server_canary_target_group_arn" {
  value = aws_lb_target_group.http_server_canary.arn
}
