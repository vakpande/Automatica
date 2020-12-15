import json
import os
import traceback

import requests

try:
    from JumpboxCreate import create_jumpbox, create_sg, delete_sg, delete_jumpbox
    from lib.db import Util
except:
    from tasks.JumpboxCreate import create_jumpbox, create_sg, delete_sg, delete_jumpbox
    from tasks.lib.db import Util

import time


# Create jumpbox

def post(params):
    url = '{}/production/api/emailservice/'.format(os.environ['API_URL'])
    print(url)
    print(params)
    requests.post(url, data=params)


dep_type = 'SESSION'

while (True):
    try:
        query = "SELECT * FROM public.\"JumpboxToCreate\""

        jumpboxes = Util.execute_query(query, dep_type)
        access_key_id = os.environ['PRODUCTION_AWS_ACCESS_KEY']
        secret_access_key = os.environ['PRODUCTION_AWS_SECRET_KEY']
        vpc_id = os.environ['JUMPBOX_VPC_ID']

        print("No, of Jumpbox to create  {}".format(len(jumpboxes)))
        for jumpbox in jumpboxes:
            instanceid, response = create_jumpbox(access_key_id, secret_access_key, jumpbox['user'])
            user_access_key = response['AccessKey']['AccessKeyId']
            user_secret_access_key = response['AccessKey']['SecretAccessKey']
            creds = {}
            creds['AccessKeyId'] = user_access_key
            creds['SecretAccessKey'] = user_secret_access_key

            print("Created Instance  {}".format(instanceid))
            query = "select * from mark_jumpbox_created({},'{}','automation', '{}')".format(jumpbox['id'], instanceid,
                                                                                            json.dumps(creds))
            Util.execute(query, dep_type)
            print("Updated Jumpbox in db with id  {}".format(jumpbox['id']))

        query = "SELECT * FROM public.\"AccessToCreate\""
        accesses = Util.execute_query(query, dep_type)
        print("No. of accesses to create  {}".format(len(accesses)))
        for access in accesses:

            sgid = create_sg(vpc_id, access['ipaddresses'], access_key_id, secret_access_key,
                             "_{}_{}".format(access['user'], access['did']),
                             access['instanceid'])
            print("Created sg  {}".format(sgid))
            query = "select * from mark_sg_created({},'{}','automation')".format(access['id'], sgid)
            Util.execute(query, dep_type)
            print("access['ipaddresses']")
            print(access['ipaddresses'])
            params = {"AccessKeyId": access['creds']['AccessKeyId'],
                      "SecretAccessKey": access['creds']['SecretAccessKey'],
                      "User": access['user'],
                      "podip": json.dumps(access['ipaddresses']),
                      "Type": "complete",
                      "did":  access['did'],
                      "accessId":  access['id'],
                      "podName": access['podname'],
                      "InstanceId": access['instanceid']}
            post(params)

            print("Updated access in db with id  {}".format(access['id']))

        query = "SELECT * FROM public.\"AccessToDelete\""
        accesses = Util.execute_query(query, dep_type)
        print("No. of accesses to delete  {}".format(len(accesses)))
        for access in accesses:
            delete_sg(access['sgid'], access_key_id, secret_access_key, access['instanceid'])
            print(" sg deleted  {}".format(access['sgid']))
            query = "select * from mark_sg_deleted({},'automation')".format(access['id'])
            Util.execute(query, dep_type)
            print("Updated access in db with id  {}".format(access['id']))

        query = "SELECT * FROM public.\"JumpboxToDelete\""
        jumpboxes = Util.execute_query(query, dep_type)
        print("No. of jumpboxes to delete  {}".format(len(jumpboxes)))
        for jumpbox in jumpboxes:
            delete_jumpbox(jumpbox['instanceid'], access_key_id, secret_access_key, jumpbox['user'], jumpbox['creds'])
            print(" jumpbox deleted  {}".format(jumpbox['instanceid']))
            query = "select * from mark_jumpbox_deleted({},'automation')".format(jumpbox['id'])
            Util.execute(query, dep_type)
            print("Updated jumpbox in db with id  {}".format(jumpbox['id']))
    except Exception as error:
        traceback.print_exc()
        print(error)

    time.sleep(15)
