resource "aws_vpc" "vpc" {
  cidr_block = "${var.vpc_cidr_block}/${var.vpc_cidr_netmask}"
  enable_dns_hostnames = true
  tags = {
    Name = "${var.vpc_name}"
  }
}

resource "aws_vpc_dhcp_options" "vpc_options" {
  domain_name = "${var.dhcp_domain_name}"
  domain_name_servers = ["AmazonProvidedDNS"]
  tags = {
    Name = "${var.vpc_name}"
  }
}
