provider "aws" {
  region = "${var.region}"
  profile = "${var.aws_credentials_profile}"
  version = "~> 2.0"
}
