data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/s3/neo4j_backups/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_s3_bucket" "backups" {
  bucket = "book-prod-neo-backups"

  tags = {
    Name        = "Backups for Neo4j"
    Environment = "Prod"
  }

}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.backups.id
  policy = file("iam_policy.json")
}

resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id = "delete-old-backups-rule"
    
    filter {
      prefix = "neo4j/"
    }
    
    expiration {
      days = 7
    }

    status = "Enabled"
  }
}