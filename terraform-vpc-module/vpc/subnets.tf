resource "aws_subnet" "untrusted-subnets" {
    vpc_id            = "${aws_vpc.vpc.id}"
    count             = "${var.subnet_count}"
    cidr_block        = "${cidrsubnet(var.vpc_cidr_full, var.vpc_cidr_bits, count.index)}"
    availability_zone = "${element(data.aws_availability_zones.available.names, count.index)}"
    tags = {
        Name          = "${var.vpc_name}.untrusted (${element(data.aws_availability_zones.available.names, count.index)})"
    }
}

resource "aws_subnet" "trusted-subnets" {
    vpc_id            = "${aws_vpc.vpc.id}"
    count             = "${var.subnet_count}"
    cidr_block        = "${cidrsubnet(var.vpc_cidr_full, var.vpc_cidr_bits, count.index + length(data.aws_availability_zones.available.names))}"
    availability_zone = "${element(data.aws_availability_zones.available.names, count.index)}"
    tags = {
        Name          = "${var.vpc_name}.trusted (${element(data.aws_availability_zones.available.names, count.index)})"
    }
}
