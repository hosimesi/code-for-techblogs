variable "private_subnets" {
  description = "List of private subnet ids to place to predictor"
}

variable "http_server_security_group" {
  description = "Security group id for http server"
}

variable "http_server_target_group_arn" {
  description = "target group for http server load balancer"
}

variable "http_server_canary_target_group_arn" {
  description = "target group for http server canary load balancer"
}

variable "http_server_ecr_uri" {
  description = "ECR URI for http server ecs task"
}

variable "http_server_canary_ecr_uri" {
  description = "ECR URI for http server canary ecs task"
}


variable "ecs_task_role_arn" {
  description = "IAM Role for ecs task application"
}

variable "ecs_task_execution_role_arn" {
  description = "IAM Role for ecs task execution"
}
