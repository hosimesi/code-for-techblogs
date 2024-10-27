# ALB for HTTP Server
resource "aws_lb" "http_server" {
  load_balancer_type = "application"
  name               = "http-server-alb"

  security_groups = ["${var.http_server_alb_security_group}"]
  subnets         = var.alb_subnets
}

resource "aws_lb_target_group" "http_server" {
  name = "http-server-tg"

  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    port = 8080
    path = "/"
  }
}

resource "aws_lb_listener" "http_server" {
  load_balancer_arn = aws_lb.http_server.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.http_server.arn
  }
}


resource "aws_lb_listener_rule" "http_server" {
  listener_arn = aws_lb_listener.http_server.arn

  action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.http_server.arn
        weight = 90
      }
      target_group {
        arn    = aws_lb_target_group.http_server_canary.arn
        weight = 10
      }
    }
  }

  condition {
    path_pattern {
      values = ["/"]
    }
  }
}


resource "aws_lb_target_group" "http_server_canary" {
  name = "http-server-canary-tg"

  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    port = 8080
    path = "/"
  }
}
