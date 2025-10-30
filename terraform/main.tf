# main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}

##############################
# IAM Role and Policy for EC2
##############################

# IAM Role for EC2 to access Secrets Manager
resource "aws_iam_role" "chatbot_role" {
  name = "chatbot-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Policy allowing access to the secret
resource "aws_iam_policy" "chatbot_secret_policy" {
  name        = "chatbot-secret-policy"
  description = "Allow EC2 to read chatbot secrets"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["secretsmanager:GetSecretValue"]
        Effect   = "Allow"
        Resource = "arn:aws:secretsmanager:*:*:secret:chatbot_backend_secrets_2*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "attach_secret_policy" {
  role       = aws_iam_role.chatbot_role.name
  policy_arn = aws_iam_policy.chatbot_secret_policy.arn
}

# Create an IAM instance profile for the EC2 instance
resource "aws_iam_instance_profile" "chatbot_profile" {
  name = "chatbot-instance-profile"
  role = aws_iam_role.chatbot_role.name
}

##############################
# Networking
##############################

# Get the default VPC
data "aws_vpc" "default" {
  default = true
}

# Get all subnets in default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security group for chatbot EC2
resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot_sg"
  description = "Allow HTTP and SSH"
  vpc_id      = data.aws_vpc.default.id

  # SSH from anywhere (for testing) — consider restricting to your IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

##############################
# Fetch latest Amazon Linux 2 AMI
##############################

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

##############################
# EC2 Instance
##############################

resource "aws_instance" "chatbot_server" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t2.micro"
  iam_instance_profile   = aws_iam_instance_profile.chatbot_profile.name
  subnet_id              = element(data.aws_subnets.default.ids, 0)
  vpc_security_group_ids = [aws_security_group.chatbot_sg.id]
  key_name               = var.key_pair_name

  user_data = file("user_data.sh")

  tags = {
    Name = "chatbot-backend"
  }
}
