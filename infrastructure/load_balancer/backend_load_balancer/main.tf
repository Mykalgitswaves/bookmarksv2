data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/load_balancer/backend_load_balancer/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_lb" "backend_load_balancer" {
  name               = "backend-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-0869975039d65a934"]
  subnets            = ["subnet-00dc7be2febbff5e2","subnet-0abc8dffd75454342"]

  tags = {
    Environment = "production"
  }
}

data "aws_secretsmanager_secret" "custom_header_secret" {
  name = "prod/custom_headers"
}

data "aws_secretsmanager_secret_version" "custom_header_secret_data" {
  secret_id = data.aws_secretsmanager_secret.custom_header_secret.id
}

locals {
  header_data = jsondecode(data.aws_secretsmanager_secret_version.custom_header_secret_data.secret_string)
}

resource "aws_lb_target_group" "backend_target_group" {
  name     = "backend-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = "vpc-0de1958ab90b56cf7"

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400  # Duration in seconds (1 day)
  }

  health_check {
    path = "/api/health/"
    port = 80
    healthy_threshold = 2
    unhealthy_threshold = 2
    timeout = 5
    interval = 60
    matcher = "200"
  }
}

resource "aws_lb_listener" "backend_listener" {
  load_balancer_arn = aws_lb.backend_load_balancer.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = "arn:aws:acm:us-east-1:788511695961:certificate/c6397802-86b3-4fa9-96a6-a3a0c12f6ded"

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "Access Denied"
      status_code  = "403"
    }
  }
}

resource "aws_lb_listener_rule" "custom_header_rule" {
  listener_arn = aws_lb_listener.backend_listener.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend_target_group.arn
  }

  condition {
    http_header {
      http_header_name = local.header_data["HEADER_NAME"]
      values           = [local.header_data["HEADER_VALUE"]]
    }
  }
}

output "load_balancer_arn" {
  value = aws_lb.backend_load_balancer.arn
}

output "target_group_arn" {
  value = aws_lb_target_group.backend_target_group.arn
}