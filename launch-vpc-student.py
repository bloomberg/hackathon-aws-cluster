#!/usr/bin/python

from __future__ import print_function
import sys
import boto3

region = 'eu-west-1'
studentNodeImageId = 'ami-88aef7fb'
controlNodeInstanceType = 'm3.xlarge'
controlNodeDiskSize = '16'
workerNodeInstanceType = 'm3.large'
workerNodeDiskSize = '16'

studentNumber = sys.argv[1]

cf = boto3.client(region_name = region, service_name = 'cloudformation')

st = cf.describe_stacks(StackName = 'jepsen')

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

with open('jepsen-vpc-student.json', 'r') as template_file:
    studentTemplate = template_file.read()

print('Creating VPC stack')

stackName = 'student-' + studentNumber

st = cf.create_stack(StackName = stackName,
                     TemplateBody = studentTemplate,
                     Parameters = [
                       { "ParameterKey": "KeyName", "ParameterValue": keyName },
                       { "ParameterKey": "Bucket", "ParameterValue": bucket },
                       { "ParameterKey": "IamProfile", "ParameterValue": iamProfile },
                       { "ParameterKey": "ControlInstanceType", "ParameterValue": controlNodeInstanceType },
                       { "ParameterKey": "ControlDiskSize", "ParameterValue": controlNodeDiskSize },
                       { "ParameterKey": "WorkerInstanceType", "ParameterValue": workerNodeInstanceType },
                       { "ParameterKey": "WorkerDiskSize", "ParameterValue": workerNodeDiskSize },
                       { "ParameterKey": "ImageId", "ParameterValue": studentNodeImageId },
                       { "ParameterKey": "SubnetNumber", "ParameterValue": studentNumber },
                       { "ParameterKey": "VpcId", "ParameterValue": vpcId },
                       { "ParameterKey": "SecGroupAccess", "ParameterValue": secGroupAccess },
                       { "ParameterKey": "RouteTable", "ParameterValue": privateRouteTable }
                     ]
                     )

stwaiter = cf.get_waiter('stack_create_complete')

print('Waiting for stack creation to be complete...')

stwaiter.wait(StackName = stackName)

print('Stack creation complete')
