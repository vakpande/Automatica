"""
Created on Fri Mar 20 12:27:58 2020

@author: vaibhavpandey
"""

import json
import boto3

def create_sg(vpc, pod_ip, access_key_id, secret_access_key, sg_postfix, instance_id):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    client = session.client('ec2')

    response = client.create_security_group(GroupName='SG_FOR_JUMPBOX_ACCESS{}'.format(sg_postfix),
                                            Description='SG_FOR_JUMPBOX_ACCESS',
                                            VpcId=vpc)
    security_group_id = response['GroupId']
    client.revoke_security_group_egress(
        DryRun=False,
        GroupId=security_group_id,
        IpPermissions=[
            {
                'FromPort': -1,
                'IpProtocol': '-1',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0'
                    },
                ],
                'ToPort': -1,
            },
        ]
    )

    for ip in pod_ip:
        cidr = ip + "/32"
        description = 'Description'
        client.authorize_security_group_egress(
            DryRun=False,
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': cidr,
                            'Description': description
                        },
                    ]
                }
            ]
        )

    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)
    sgids = [sg['GroupId'] for sg in instance.security_groups]
    sgids.append(security_group_id)
    instance.modify_attribute(Groups=sgids)
    return security_group_id


def get_jumpbox_state(access_key_id, secret_access_key):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    client = session.client('ec2')

    custom_filter = [{
        'Name': 'tag:Owner',
        'Values': ['vaibhavp']}]

    response = client.describe_instances(Filters=custom_filter)

    instance_id = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instance_id.apend(instance["InstanceId"])

    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id[0])
    status = instance.state['Name']
    return status


def create_jumpbox(access_key_id, secret_access_key, user):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    ec2 = session.resource('ec2')
    jumpbox = ec2.create_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {

                    'DeleteOnTermination': True,
                    'VolumeSize': 8,
                    'VolumeType': 'gp2'
                },
            },
        ],
        ImageId='ami-008fa27bbd0de0470',
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        SubnetId='subnet-ac0d6ef6',
        IamInstanceProfile={
            'Arn': 'arn:aws:iam::703024586312:instance-profile/session-manager'
        },
        Monitoring={
            'Enabled': False
        },
        SecurityGroupIds=['sg-0c95dabaa98f454fd'],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'Jumpbox-{}'.format(user)
                    },
                ]
            },
        ]
    )
    create_user_policy(access_key_id, secret_access_key, jumpbox[0].id, user)
    create_iam_user(access_key_id, secret_access_key, user)
    response = create_access_key(access_key_id, secret_access_key, user)
    return jumpbox[0].id, response


def delete_jumpbox(instance_id, access_key_id, secret_access_key, user, creds):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)
    if instance.state['Name'] == 'running':
        ec2.instances.filter(InstanceIds=[instance_id]).terminate()
    else:
        print("instance already terminated")
    delete_iam_user(access_key_id, secret_access_key, user, creds)


def delete_sg(security_group_id, access_key_id, secret_access_key, instance_id):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    client = session.client('ec2')
    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)
    sgids = [sg['GroupId'] for sg in instance.security_groups]
    sgids.remove(security_group_id)
    sgids = ['sg-b95f73c7'] if len(sgids) == 0 else sgids
    instance.modify_attribute(Groups=sgids)
    client.delete_security_group(GroupId=security_group_id)


def create_user_policy(access_key_id, secret_access_key, instance_id, user):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')
    iam = session.resource('iam')
    Policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "ssm:StartSession",
                "Resource": [
                    "arn:aws:ec2:*:*:instance/{}".format(instance_id),
                    "arn:aws:ssm:*:*:document/AWS-StartSSHSession"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetEncryptionConfiguration"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "kms:GenerateDataKey*"
                ],
                "Resource": "arn:aws:kms:us-west-2:703024586312:key/871248e1-7941-4730-a6c9-e96737b829dc"
            }
        ]
    }

    iam.create_policy(
        PolicyName='Jumpbox-{}'.format(user),
        Description='ssm-policy',
        PolicyDocument=json.dumps(Policy)
    )


def create_iam_user(access_key_id, secret_access_key, user):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    iam = session.client('iam')
    iam.create_user(UserName=user)

    iam.attach_user_policy(
        UserName=user,
        PolicyArn='arn:aws:iam::703024586312:policy/Jumpbox-{}'.format(user)
    )


def create_access_key(access_key_id, secret_access_key, user):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    iam = session.client('iam')
    response = iam.create_access_key(UserName=user)
    create_client_script(response, user)
    return response


def delete_iam_user(access_key_id, secret_access_key, user, creds):
    session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,
                            region_name='us-west-2')

    iam = session.client('iam')
    iam.detach_user_policy(
        UserName=user,
        PolicyArn='arn:aws:iam::703024586312:policy/Jumpbox-{}'.format(user)
    )
    iam.delete_policy(
        PolicyArn='arn:aws:iam::703024586312:policy/Jumpbox-{}'.format(user)
    )
    iam.delete_access_key(UserName=user, AccessKeyId=creds['AccessKeyId'])
    iam.delete_user(UserName=user)
    delete_client_script(user)


def create_client_script(response, user):
    AccessKeyId = response['AccessKey']['AccessKeyId']
    SecretAccessKey = response['AccessKey']['SecretAccessKey']

    with open('{}-client.sh'.format(user), 'w') as rsh:
        rsh.write(
            '''\
    #!/bin/bash
    if session-manager-plugin  | grep 'Session Manager plugin was installed successfully'; then
        echo "The Session Manager plugin was installed successfully. Use the AWS CLI to start a session."
    else
        curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip" -o "sessionmanager-bundle.zip"
        unzip sessionmanager-bundle.zip
        sudo ./sessionmanager-bundle/install -i /usr/local/sessionmanagerplugin -b /usr/local/bin/session-manager-plugin
    fi

    if echo "which aws" | grep aws; then
        echo "awscli is installed. configure the aws environment"
    else
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
    fi

    echo "aws configure set aws_access_key_id {}" .format(AccessKeyId)
    echo "aws configure set aws_secret_access_key {}" .format(SecretAccessKey)
    echo "aws configure set default.region us-west-2"
       ''' )

def delete_client_script(user):
    pass