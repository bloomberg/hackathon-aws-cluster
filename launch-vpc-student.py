#!/usr/bin/python

from __future__ import print_function
import sys
import boto3
import concurrent.futures

region = 'us-east-1'
studentNodeImageId = 'ami-a28a58b4'
controlNodeInstanceType = 'c4.4xlarge'
controlNodeDiskSize = '32'

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

def launch_student(studentNumber):
    print('Creating VPC stack for student', studentNumber)

    stackName = 'student-' + studentNumber

    st = cf.create_stack(StackName = stackName,
                         TemplateBody = studentTemplate,
                         Parameters = [
                             { "ParameterKey": "KeyName", "ParameterValue": keyName },
                             { "ParameterKey": "Bucket", "ParameterValue": bucket },
                             { "ParameterKey": "IamProfile", "ParameterValue": iamProfile },
                             { "ParameterKey": "ControlInstanceType", "ParameterValue": controlNodeInstanceType },
                             { "ParameterKey": "ControlDiskSize", "ParameterValue": controlNodeDiskSize },
                             { "ParameterKey": "ImageId", "ParameterValue": studentNodeImageId },
                             { "ParameterKey": "SubnetNumber", "ParameterValue": studentNumber },
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

st = cf.describe_stacks(StackName = 'coa')

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

with open('coa-vpc-student.json', 'r') as template_file:
    studentTemplate = template_file.read()

with concurrent.futures.ThreadPoolExecutor(max_workers = (end - start) + 1) as executor:
    fs = { executor.submit(wait_on_stack, launch_student(str(x))) for x in range(start, end + 1) }
    print('Waiting for stack creation to be complete...')
    concurrent.futures.wait(fs)

print('Stack creation complete')
