

resource "aws_instance" "bastions" {
  ami                      = "ami-51537029"
  count                    = "${var.bastion == 1 ? 3 : 0}"
  instance_type            = "t2.medium"
  key_name                 = "opskey"
  iam_instance_profile     = "${aws_iam_instance_profile.bastions.name}"
  vpc_security_group_ids   = ["${aws_security_group.bastion[count.index]}"]
  subnet_id                = "${aws_subnet.trusted-subnets.*.id[count.index]}"
  private_ip               = "${cidrhost(element(data.aws_subnet.trusted_subnets.*.cidr_block, count.index), 4)}"
  user_data = <<EOF
#!/bin/bash
sleep 10s
mkdir /home/ubuntu/scripts
sudo apt-get update && sudo apt-get -y install awscli
sudo apt-get install -y python-pip python-dev build-essential
sudo pip install ansible
sudo echo '${data.template_file.bastion.rendered}' > /home/ubuntu/scripts/bastion.yaml
sudo ansible-playbook -i "localhost," -c local /home/ubuntu/scripts/bastion.yaml
  EOF

  tags = {
      role = "bastion"
      cluster = "ops"
    }
  
  lifecycle {
    ignore_changes = [
      "tags"
    ]
  }
}
