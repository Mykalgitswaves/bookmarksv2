data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/lambda/replace_backend/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

data "aws_iam_role" "lambda_role" {  
  name = "lambda-role-basic"
}

data "archive_file" "python_lambda_package" {  
  type = "zip"  
  source_file = "${path.module}/code/lambda_function.py" 
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "replace_backend_lambda_function" {
        function_name = "replace_backend_lambda_function"
        filename      = "lambda_function.zip"
        source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
        role          = data.aws_iam_role.lambda_role.arn
        runtime       = "python3.10"
        handler       = "lambda_function.lambda_handler"
        timeout       = 100
}