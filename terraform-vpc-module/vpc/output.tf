output "trusted-subnets" {
  value = "${aws_subnet.trusted-subnets.*.id}"
}

output "trusted_subnet_cidrs" {
  value = "${aws_subnet.trusted-subnets.*.cidr_block}"
}

output "vpc_id" {
  value = "${aws_vpc.vpc.id}"
}

output "trusted_rt" {
  value = "${aws_route_table.trusted.id}"
}

output "vpc_cidr" {
  value = "${aws_vpc.vpc.cidr_block}"
}
