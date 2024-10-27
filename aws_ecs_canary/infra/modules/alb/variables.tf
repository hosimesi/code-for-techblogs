variable "http_server_alb_security_group" {
  description = "Security group id for http server alb"
}

variable "alb_subnets" {
  description = "List of public subnet ids to place to application load balancer"
}

variable "vpc_id" {
  description = "VPC ID to place target group"
}
