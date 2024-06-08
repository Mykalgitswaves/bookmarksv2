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

resource "aws_s3_bucket_website_configuration" "website_config" {
  bucket = aws_s3_bucket.front_end.id

  index_document {
    suffix = "index.html"
  }

  # error_document {
  #   key = "error.html"
  # }

   routing_rule {
    condition {
      key_prefix_equals = "dist/"
    }
    redirect {
      replace_key_prefix_with = "/"
    }
  }
}

resource "aws_cloudfront_origin_access_identity" "my_oai" {
  comment = "My OAI for S3 bucket"
}

resource "aws_cloudfront_distribution" "my_distribution" {
  origin {
    domain_name = "${aws_s3_bucket.front_end.bucket_regional_domain_name}"
    origin_id   = "book-prod-front-end-static-files-origin"

    s3_origin_config {
      origin_access_identity =  aws_cloudfront_origin_access_identity.my_oai.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "book-prod-front-end-static-files-origin"

    forwarded_values {
      query_string = true   

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.my_distribution.domain_name
}