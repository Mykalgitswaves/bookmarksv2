data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/s3/front_end_static_files/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_s3_bucket" "front_end" {
  bucket = "book-prod-front-end-static-files"

  tags = {
    Name        = "Static Files for Front End"
    Environment = "Prod"
  }
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.front_end.id
  policy = file("iam_policy.json")
}
