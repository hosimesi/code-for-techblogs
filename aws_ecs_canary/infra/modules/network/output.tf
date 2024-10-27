output "public_subnets" {
  value = ["${aws_subnet.public1a.id}", "${aws_subnet.public1c.id}", "${aws_subnet.public1d.id}"]
}

output "private_subnets" {
  value = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
}

output "http_server_alb_security_group" {
  value = aws_security_group.http_server_alb.id
}

output "http_server_security_group" {
  value = aws_security_group.http_server.id
}

output "vpc_id" {
  value = aws_vpc.http_server.id
}

output "http_server_subnet" {
  value = aws_subnet.private1a.id
}
