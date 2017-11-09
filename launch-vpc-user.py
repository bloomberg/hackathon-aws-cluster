#!/usr/bin/python

from __future__ import print_function
import sys
import boto3
import concurrent.futures

region = 'eu-west-1'
userNodeImageId = 'ami-ff2c8086'
userNodeInstanceType = 'c5.xlarge'
userNodeDiskSize = '32'

argc = len(sys.argv) - 1
if argc == 1:
    start = int(sys.argv[1])
    end = start
elif argc == 2:
    start = int(sys.argv[1])
    end = int(sys.argv[2])
else:
    print("One or two arguments must be supplied.")
    sys.exit()

def launch_user(userNumber):
    print('Creating VPC stack for user', userNumber)

    stackName = 'user-' + userNumber

    st = cf.create_stack(StackName = stackName,
                         TemplateBody = userTemplate,
                         Parameters = [
                             { "ParameterKey": "KeyName", "ParameterValue": keyName },
                             { "ParameterKey": "Bucket", "ParameterValue": bucket },
                             { "ParameterKey": "IamProfile", "ParameterValue": iamProfile },
                             { "ParameterKey": "InstanceType", "ParameterValue": userNodeInstanceType },
                             { "ParameterKey": "DiskSize", "ParameterValue": userNodeDiskSize },
                             { "ParameterKey": "ImageId", "ParameterValue": userNodeImageId },
                             { "ParameterKey": "SubnetNumber", "ParameterValue": userNumber },
                             { "ParameterKey": "VpcId", "ParameterValue": vpcId },
                             { "ParameterKey": "SecGroupAccess", "ParameterValue": secGroupAccess },
                             { "ParameterKey": "RouteTable", "ParameterValue": privateRouteTable }
                             ]
                         )

    stwaiter = cf.get_waiter('stack_create_complete')

    return (stackName, stwaiter)

def wait_on_stack(t):
    t[1].wait(StackName = t[0])
    print("Stack", t[0], "complete")

cf = boto3.client(region_name = region, service_name = 'cloudformation')

st = cf.describe_stacks(StackName = 'git')

outputs = st['Stacks'][0]['Outputs']

for out in outputs:
    if out['Description'] == 'PrivateRouteTable':
        privateRouteTable = out['OutputValue']
    elif out['Description'] == 'VpcId':
        vpcId = out['OutputValue']
    elif out['Description'] == 'SecGroupAccess':
        secGroupAccess = out['OutputValue']
    elif out['Description'] == 'KeyName':
        keyName = out['OutputValue']
    elif out['Description'] == 'Bucket':
        bucket = out['OutputValue']
    elif out['Description'] == 'IamProfile':
        iamProfile = out['OutputValue']

with open('git-vpc-user.json', 'r') as template_file:
    userTemplate = template_file.read()

with concurrent.futures.ThreadPoolExecutor(max_workers = (end - start) + 1) as executor:
    fs = { executor.submit(wait_on_stack, launch_user(str(x))) for x in range(start, end + 1) }
    print('Waiting for stack creation to be complete...')
    concurrent.futures.wait(fs)

print('Stack creation complete')
