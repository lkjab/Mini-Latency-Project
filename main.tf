provider "aws" {
  region = "us-east-1"
}

# 1. DATA: Look up the Default VPC and its Subnets
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  # My AMI does not exist in us-east-1e, so we exclude that AZ
  filter {
    name   = "availability-zone"
    # We list every AZ EXCEPT us-east-1e
    values = ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1f"]
  }
}

data "aws_subnet" "each_subnet" {
  for_each = toset(data.aws_subnets.default.ids)
  id       = each.value
}

# 2. SECURITY GROUP: Allow all inbound and outbound traffic
resource "aws_security_group" "prober_sg" {
  name        = "latency-prober-sg-simple"
  description = "Allow SSH inbound for probers"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. RESOURCE: One Instance per Subnet
resource "aws_instance" "probers" {
  for_each = data.aws_subnet.each_subnet

  ami                         = "ami-07ff62358b87c7116" # Amazon Linux 2023
  instance_type               = "t3.micro"
  key_name                    = "probingproject" 
  vpc_security_group_ids      = [aws_security_group.prober_sg.id]
  subnet_id                   = each.value.id
  associate_public_ip_address = true

  # USER DATA: Installs Nmap (which includes nping) and mtr
  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y nmap mtr
              EOF

  tags = {
    Name = "Prober-${each.value.availability_zone}"
  }
}

resource "aws_instance" "mock_exchange" {
  ami                         = "ami-07ff62358b87c7116" # Amazon Linux 2023
  instance_type               = "t3.micro"
  key_name                    = "probingproject"
  vpc_security_group_ids      = [aws_security_group.prober_sg.id]
  associate_public_ip_address = true

    user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y nmap mtr
              EOF

  tags = {
    Name = "Mock-Exchange"
  }
}

# 4. OUTPUTS: Quick connection strings
output "instance_ips" {
  value = {
    for p in aws_instance.probers : p.tags["Name"] => p.public_ip
  }
}

output "mock_exchange_ip" {
  value = aws_instance.mock_exchange.public_ip
}
