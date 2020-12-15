resource "aws_nat_gateway" "natgw" {
  allocation_id = "${aws_eip.natgw.id}"
  subnet_id     = "${aws_subnet.untrusted-subnets.0.id}"

  tags = {
    Name = "${var.vpc_name}-natgw"
  }
}
