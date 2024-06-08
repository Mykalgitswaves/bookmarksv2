data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/event_bridge/schedule_backend_replace/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_iam_role" "eventbridge_role" {
  name = "eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_policy" {
  name   = "eventbridge-policy"
  role   = aws_iam_role.eventbridge_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "states:StartExecution"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:states:us-east-1:788511695961:stateMachine:backend-replace-state-machine"
      }
    ]
  })
}

resource "aws_cloudwatch_event_rule" "trigger_step_function" {
  name                = "TriggerStepFunctionAt5AM_EST"
  description         = "Triggers the Step Function at 5:00 AM EST daily"
  schedule_expression = "cron(00 10 * * ? *)"  # 10:00 AM UTC (5:00 AM EST)
  state          = "DISABLED"
}

resource "aws_cloudwatch_event_target" "step_function_target" {
  rule      = aws_cloudwatch_event_rule.trigger_step_function.name
  arn       = "arn:aws:states:us-east-1:788511695961:stateMachine:backend-replace-state-machine"
  target_id = "StepFunctionTarget"
  role_arn = aws_iam_role.eventbridge_role.arn
}