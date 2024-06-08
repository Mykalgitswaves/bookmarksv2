data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/user/github_user/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_iam_policy" "enable_eventbridge_rule_policy" {
  name        = "EnableEventBridgeRulePolicy"
  description = "Policy to allow enabling of EventBridge rule"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "events:EnableRule",
        Effect   = "Allow",
        Resource = "arn:aws:events:us-east-1:788511695961:rule/TriggerStepFunctionAt5AM_EST"
      }
    ]
  })
}

resource "aws_iam_policy" "get_github_secrets_policy" {
  name        = "GetGithubSecretsPolicy"
  description = "Policy to allow Get for Github secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
            Action   = "secretsmanager:GetSecretValue",
            Effect   = "Allow",
            Resource = "arn:aws:secretsmanager:us-east-1:788511695961:secret:dev/github-workflow-secrets-S6hWe8"
        }
    ]
  })
}

resource "aws_iam_policy" "deploy_front_end_static_files_policy" {
  name        = "DeployFrontEndStaticFilesPolicy"
  description = "Policy to allow deployment of front end static files"

  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::book-prod-front-end-static-files",
        "arn:aws:s3:::book-prod-front-end-static-files/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "arn:aws:cloudfront::788511695961:distribution/EWRREJ7Z0ZU5W"
    }
  ]
}
)
}

resource "aws_iam_user" "github_actions_user" {
  name = "github_actions_user"
}

resource "aws_iam_user_policy_attachment" "github_actions_user_policy_attachment" {
  user       = aws_iam_user.github_actions_user.name
  policy_arn = aws_iam_policy.enable_eventbridge_rule_policy.arn
}

resource "aws_iam_user_policy_attachment" "github_actions_user_policy_attachment_2" {
  user       = aws_iam_user.github_actions_user.name
  policy_arn = aws_iam_policy.get_github_secrets_policy.arn
}

resource "aws_iam_user_policy_attachment" "github_actions_user_policy_attachment_3" {
  user       = aws_iam_user.github_actions_user.name
  policy_arn = aws_iam_policy.deploy_front_end_static_files_policy.arn
}

resource "aws_iam_access_key" "github_actions_user_access_key" {
  user = aws_iam_user.github_actions_user.name
}

output "github_actions_user_access_key_id" {
  value = aws_iam_access_key.github_actions_user_access_key.id
}

output "github_actions_user_secret_access_key" {
  value     = aws_iam_access_key.github_actions_user_access_key.secret
  sensitive = true
}