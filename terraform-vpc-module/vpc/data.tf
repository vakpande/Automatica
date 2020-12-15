data "aws_availability_zones" "available" {}

data "template_file" "bastion" {
  template = "${file("${path.module}/templates/bastion.yaml")}"

  vars = {
    region = "${var.region}"
  }
}

data "aws_ami" "xenial" {
    most_recent = true

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-*"]
    }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }

    owners = ["099720109477"] # Canonical
}

data "aws_subnet" "trusted_subnets" {
  count = 3
  id = "${aws_subnet.trusted-subnets.*.id[count.index]}"
}