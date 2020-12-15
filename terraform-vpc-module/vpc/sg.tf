resource "aws_security_group" "bastion" {
  vpc_id = "${aws_vpc.vpc.id}"
  name = "bastion-${var.vpc_name}"
  count = "${var.bastion == 1 ? 1 : 0}"
  description = "bastion.${var.vpc_name}"

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    self = true
    cidr_blocks = ["10.199.0.45/32"]
  }

  tags = {
    Name = "bastion-${var.vpc_name}"
  }
}
