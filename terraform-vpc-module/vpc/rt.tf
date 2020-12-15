resource "aws_route_table" "trusted" {
  vpc_id = "${aws_vpc.vpc.id}"

  tags = {
    Name = "${var.vpc_name}.trusted"
  }
}

resource "aws_route_table" "untrusted" {
  vpc_id = "${aws_vpc.vpc.id}"

  tags = {
    Name = "${var.vpc_name}.untrusted"
  }
}

resource "aws_route" "untrusted-1" {
  route_table_id            = "${aws_route_table.untrusted.id}"
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id = "${aws_internet_gateway.igw.id}"
}

resource "aws_route" "trusted-1" {
  route_table_id            = "${aws_route_table.trusted.id}"
  destination_cidr_block    = "0.0.0.0/0"
  nat_gateway_id = "${aws_nat_gateway.natgw.id}"
}

#resource "aws_main_route_table_association" "main" {
#  vpc_id         = "${aws_vpc.vpc.id}"
#  route_table_id = "${aws_route_table.trusted.id}"
#}

resource "aws_route_table_association" "untrusted" {
    count          = "${var.subnet_count}"
    subnet_id      = "${element(aws_subnet.untrusted-subnets.*.id, count.index)}"
    route_table_id = "${aws_route_table.untrusted.id}"
}

resource "aws_route_table_association" "trusted" {
    count          = "${var.subnet_count}"
    subnet_id      = "${element(aws_subnet.trusted-subnets.*.id, count.index)}"
    route_table_id = "${aws_route_table.trusted.id}"
}
