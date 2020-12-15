resource "aws_iam_instance_profile" "bastions" {
  name  = "bastions_profile"
  role = "${aws_iam_role.bastions.name}"
}


resource "aws_iam_role_policy" "bastions_iam_role_policy" {
  name = "bastions-iam-role-policy"
  role = "${aws_iam_role.bastions.id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1521566048462",
      "Action": [
        "ec2:CreateTags",
        "ec2:DeleteTags",
        "ec2:DescribeHosts",
        "ec2:DescribeInstances",
        "ec2:DescribeTags",
        "ec2:ModifyInstanceAttribute",
        "support:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}



resource "aws_iam_role" "bastions" {
    name = "bastions"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "apt-repo" {
    role       = "${aws_iam_role.bastions.name}"
    policy_arn = "${var.apt_policy_arn}"
}

resource "aws_iam_role_policy_attachment" "credstash-readonly" {
    role       = "${aws_iam_role.bastions.name}"
    policy_arn = "${var.credstash_readonly_arn}"
}
