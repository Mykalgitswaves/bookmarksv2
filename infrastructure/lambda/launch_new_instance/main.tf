data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/lambda/launch_new_instance/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

data "aws_iam_policy_document" "lambda_assume_role_policy"{
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {  
  name = "lambda-role-basic"  
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

resource "aws_iam_policy" "lambda_ec2_elb_policy" {
  name        = "lambda_ec2_elb_policy"
  description = "Policy for Lambda to run EC2 instances"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "ec2:RunInstances",
          "ec2:DescribeInstances",
          "ec2:TerminateInstances",
          "ec2:StopInstances",
          "ec2:StartInstances",
          "elasticloadbalancing:RegisterTargets",
          "elasticloadbalancing:DeregisterTargets",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetHealth"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_disable_eventbridge_rule_policy" {
  name        = "LambdaDisableEventBridgeRulePolicy"
  description = "IAM policy to allow Lambda to disable EventBridge rule"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "events:DisableRule"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:events:us-east-1:788511695961:rule/TriggerStepFunctionAt5AM_EST"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_ec2_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_ec2_elb_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_event_bridge_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_disable_eventbridge_rule_policy.arn
}

data "archive_file" "python_lambda_package" {  
  type = "zip"  
  source_file = "${path.module}/code/lambda_function.py" 
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "launch_instance_lambda_function" {
        function_name = "launch_instance_lambda_function"
        filename      = "lambda_function.zip"
        source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
        role          = aws_iam_role.lambda_role.arn
        runtime       = "python3.10"
        handler       = "lambda_function.lambda_handler"
        timeout       = 100
}