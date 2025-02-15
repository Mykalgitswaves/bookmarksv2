variable "aws_region" {
  description = "AWS region where the EC2 instance will be deployed"
  default     = "us-east-1"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  default     = "ami-0e1bed4f06a3b463d" # Ubuntu 22.02
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.small"
}

variable "key_pair" {
  description = "Existing AWS SSH key pair"
  default = "bookmarks-web-server"
}

variable "subnet_id" {
  description = "ID of the existing subnet"
  default = "subnet-00dc7be2febbff5e2"
}

variable "security_group_id" {
  description = "ID of the existing security groups"
  default = ["sg-0940d2c175af8cad2", "sg-09d22bff8997e1e47"]
}

variable "user_data_script" {
  description = "Path to the user data script file"
  default     = "setup.sh"
}
