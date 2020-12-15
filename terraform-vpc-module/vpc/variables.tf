variable "vpc_name" {}

variable "region" {
  default = "us-west-2"
}

variable "aws_credentials_profile" {
  default = "ni-prod"
}

variable "vpc_cidr_block" {}

variable "vpc_cidr_netmask" {}

variable "vpc_cidr_bits" {}

variable "subnet_count" {}

variable "vpc_cidr_full" {}

variable "dhcp_domain_name" {}

variable "bastion" {}

variable "apt_policy_arn" {}

variable "credstash_readonly_arn" {}
