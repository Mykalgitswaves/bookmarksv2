data "aws_caller_identity" "current" {}

terraform {
  backend "s3" {
    bucket         	   = "terraform-backend-state-crab"
    key              	   = "src/launch_template/backend_launch_template/terraform.tfstate"
    region         	   = "us-east-1"
    encrypt        	   = true
    dynamodb_table = "terraform-backend-locks"
  }
}

resource "aws_launch_template" "backend_template" {
  name = "backend-launch-template-05-29"
  description = "Launch template for provisioning backend instances created on 5-29-2024"
  
  image_id = "ami-0aa72f978f8e15efc"
  instance_type = "t3.small"
  key_name = "bookmarks-web-server"

  update_default_version = true
  
  instance_initiated_shutdown_behavior = "terminate"

  network_interfaces {
    associate_public_ip_address = true
    delete_on_termination = true
    subnet_id = "subnet-00dc7be2febbff5e2"
    security_groups = ["sg-0940d2c175af8cad2", "sg-09d22bff8997e1e47"]
  }

  user_data = filebase64("${path.module}/setup.sh")
}
