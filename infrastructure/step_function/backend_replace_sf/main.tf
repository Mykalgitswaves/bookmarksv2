data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/step_function/backend_replace_sf/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_iam_role" "sfn_role" {
  name = "sfn_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_policy" {
  role       = aws_iam_role.sfn_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"
}

resource "aws_iam_role_policy" "sfn_lambda_invoke_policy" {
  name = "sfn_lambda_invoke_policy"
  role = aws_iam_role.sfn_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "lambda:InvokeFunction"
        ],
        Resource = [
          data.aws_lambda_function.launch_instance_lambda_function.arn,
          data.aws_lambda_function.replace_backend_lambda_function.arn
        ]
      }
    ]
  })
}

data "aws_lambda_function" "launch_instance_lambda_function" {
  function_name = "launch_instance_lambda_function"
}

data "aws_lambda_function" "replace_backend_lambda_function" {
  function_name = "replace_backend_lambda_function"
}

resource "aws_sfn_state_machine" "backend_replace" {
  name     = "backend-replace-state-machine"
  role_arn = aws_iam_role.sfn_role.arn
  definition = jsonencode({
    Comment: "A simple Step Function to wait 10 minutes between two Lambda functions",
    StartAt: "LaunchInstance",
    States: {
      LaunchInstance: {
        Type: "Task",
        Resource: data.aws_lambda_function.launch_instance_lambda_function.arn,
        Next: "Wait5Minutes"
      },
      Wait5Minutes: {
        Type: "Wait",
        Seconds: 300,
        Next: "ReplaceBackend"
      },
      "ReplaceBackend": {
        Type: "Task",
        Resource: data.aws_lambda_function.replace_backend_lambda_function.arn,
        End: true
      }
    }
  })
}
