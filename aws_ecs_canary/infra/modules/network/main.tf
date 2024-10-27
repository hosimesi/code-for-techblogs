# VPC
resource "aws_vpc" "http_server" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "http-server"
  }
}

# SecurityGroup for ALB
resource "aws_security_group" "http_server_alb" {
  name        = "http-server-alb-sg"
  description = "security group for http server alb"
  vpc_id      = aws_vpc.http_server.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "http-server-alb-sg"
  }
}


# SecurityGroup for
resource "aws_security_group" "http_server" {
  name        = "http-server-sg"
  description = "security group for http server"
  vpc_id      = aws_vpc.http_server.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = ["${aws_security_group.http_server_alb.id}"]
  }

  # Allow VPC Endpoint traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "http-server-sg"
  }
}

resource "aws_security_group" "vpc_endpoint" {
  name        = "vpc-endpoint-sg"
  description = "security group for vpc endpoint"
  vpc_id      = aws_vpc.http_server.id
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = ["${aws_security_group.http_server.id}"]
  }

  # Allow VPC Endpoint traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "vpc-endpoint-sg"
  }
}


# Public Subnet (${var.aws_region}a)
resource "aws_subnet" "public1a" {
  vpc_id            = aws_vpc.http_server.id
  availability_zone = "${var.aws_region}a"
  cidr_block        = "10.0.1.0/24"

  tags = {
    Name = "http-server-public-subnet-1a"
  }
}

# Public Subnet (${var.aws_region}c)
resource "aws_subnet" "public1c" {
  vpc_id            = aws_vpc.http_server.id
  availability_zone = "${var.aws_region}c"
  cidr_block        = "10.0.2.0/24"

  tags = {
    Name = "http-server-public-subnet-1c"
  }
}

# Public Subnet (${var.aws_region}d)
resource "aws_subnet" "public1d" {
  vpc_id            = aws_vpc.http_server.id
  availability_zone = "${var.aws_region}d"
  cidr_block        = "10.0.3.0/24"

  tags = {
    Name = "http-server-public-subnet-1d"
  }
}

# Private Subnets (${var.aws_region}a)
resource "aws_subnet" "private1a" {
  vpc_id            = aws_vpc.http_server.id
  availability_zone = "${var.aws_region}a"
  cidr_block        = "10.0.10.0/24"

  tags = {
    Name = "http-server-private-subnet-1a"
  }
}

# Private Subnets (${var.aws_region}c)
resource "aws_subnet" "private1c" {
  vpc_id            = aws_vpc.http_server.id
  availability_zone = "${var.aws_region}c"
  cidr_block        = "10.0.20.0/24"

  tags = {
    Name = "http-server-private-subnet-1c"
  }
}

# Private Subnets (${var.aws_region}d)
resource "aws_subnet" "private1d" {
  vpc_id            = aws_vpc.http_server.id
  availability_zone = "${var.aws_region}d"
  cidr_block        = "10.0.30.0/24"

  tags = {
    Name = "http-server-private-subnet-1d"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "http_server" {
  vpc_id = aws_vpc.http_server.id

  tags = {
    Name = "http-server-igw"
  }
}


# Route Table (Public)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.http_server.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.http_server.id
  }

  tags = {
    Name = "http-server-public-route"
  }
}

# Association (Public ${var.aws_region}a)
resource "aws_route_table_association" "public1a" {
  subnet_id      = aws_subnet.public1a.id
  route_table_id = aws_route_table.public.id
}

# Association (Public ${var.aws_region}c)
resource "aws_route_table_association" "public1c" {
  subnet_id      = aws_subnet.public1c.id
  route_table_id = aws_route_table.public.id
}

# Association (Public ${var.aws_region}d)
resource "aws_route_table_association" "public1d" {
  subnet_id      = aws_subnet.public1d.id
  route_table_id = aws_route_table.public.id
}


# Route Table (Private)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.http_server.id

  route {
    cidr_block = "10.0.0.0/16"
    gateway_id = "local"
  }

  tags = {
    Name = "http-server-private-route"
  }
}

# Association (Private ${var.aws_region}a)
resource "aws_route_table_association" "private1a" {
  subnet_id      = aws_subnet.private1a.id
  route_table_id = aws_route_table.private.id
}

# Association (Private ${var.aws_region}c)
resource "aws_route_table_association" "private1c" {
  subnet_id      = aws_subnet.private1c.id
  route_table_id = aws_route_table.private.id
}

# Association (Private ${var.aws_region}d)
resource "aws_route_table_association" "private1d" {
  subnet_id      = aws_subnet.private1d.id
  route_table_id = aws_route_table.private.id
}

## VPC Endpoints
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.http_server.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = ["${aws_route_table.private.id}", "${aws_route_table.public.id}"]
  tags = {
    Name = "http-server-s3-vpe"
  }
}

resource "aws_vpc_endpoint" "ecr-dkr" {
  vpc_id              = aws_vpc.http_server.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.vpc_endpoint.id}"]
  tags = {
    Name = "http-server-ecr-dkr-vpe"
  }
}

resource "aws_vpc_endpoint" "ecr-api" {
  vpc_id              = aws_vpc.http_server.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.vpc_endpoint.id}"]
  tags = {
    Name = "http-server-ecr-api-vpe"
  }
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.http_server.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.vpc_endpoint.id}"]
  tags = {
    Name = "http-server-secretsmanager-vpe"
  }
}

resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.http_server.id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.vpc_endpoint.id}"]
  tags = {
    Name = "http-server-ssm-vpe"
  }
}

resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.http_server.id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.vpc_endpoint.id}"]
  tags = {
    Name = "http-server-logs-vpe"
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.http_server.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = ["${aws_route_table.private.id}"]
  tags = {
    Name = "http-server-dynamodb-vpe"
  }
}
