resource "aws_route53_zone_association" "ni-onsaas-internal-com" {
  zone_id = "Z2TT5HAZ6DQ91N"
  vpc_id  = "${aws_vpc.vpc.id}"
}
