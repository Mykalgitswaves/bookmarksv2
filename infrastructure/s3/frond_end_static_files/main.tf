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
  web_acl_id = "arn:aws:wafv2:us-east-1:788511695961:global/webacl/clopudfront-waf/630343c7-c3ed-4027-ad63-653743a7229f"

  origin {
    domain_name = "${aws_s3_bucket.front_end.bucket_regional_domain_name}"
    origin_id   = "book-prod-front-end-static-files-origin"

    s3_origin_config {
      origin_access_identity =  aws_cloudfront_origin_access_identity.my_oai.cloudfront_access_identity_path
    }
  }

  origin {
    domain_name = "backend-load-balancer-1064516976.us-east-1.elb.amazonaws.com"
    origin_id   = "backend-load-balancer-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  ordered_cache_behavior {
    path_pattern           = "/api/*"
    target_origin_id       = "backend-load-balancer-origin"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods  = ["GET", "HEAD"]

    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    origin_request_policy_id = "216adef6-5c7f-47e4-b989-5492eafa07d3"

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "book-prod-front-end-static-files-origin"

    forwarded_values {
      query_string = true   

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  aliases = ["hardcoverlit.com","www.hardcoverlit.com"]

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA"]
    }
  }

  viewer_certificate {
    acm_certificate_arn = "arn:aws:acm:us-east-1:788511695961:certificate/c6397802-86b3-4fa9-96a6-a3a0c12f6ded"
    ssl_support_method = "sni-only"
  }
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.my_distribution.domain_name
}