# variables.tf

variable "aws_region" {
  default = "ap-northeast-1"
}

variable "ami_id" {
  # Amazon Linux 2 AMI (change region if needed)
  default = "ami-08f3d892de259504d"
}

variable "key_pair_name" {
  description = "Name of an existing AWS key pair for SSH access"
  type        = string
  default     = "chatbot_server_ec2_key"   # ✅ your key pair
}
