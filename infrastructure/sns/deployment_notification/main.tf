data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/sns/deployment_notification/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_sns_topic" "deployment_notification" {
  name = "deployment_notification"
}

output "sns_topic_arn" {
  value = aws_sns_topic.deployment_notification.arn
  
}