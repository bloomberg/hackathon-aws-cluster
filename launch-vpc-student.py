#!/usr/bin/python

from __future__ import print_function
import sys
import json
import boto3

studentNodeImageId = 'ami-88aef7fb'
controlNodeInstanceType = 'm3.xlarge'
controlNodeDiskSize = '16'
workerNodeInstanceType = 'm3.large'
workerNodeDiskSize = '16'

studentNumber = sys.argv[1]

with open('jepsen-vpc.tmp', 'r') as parms_file:
    parms = json.loads(parms_file.read())

cf = boto3.client(region_name = parms['region'], service_name = 'cloudformation')

with open('jepsen-vpc-student.json', 'r') as template_file:
    studentTemplate = template_file.read()

print('Creating VPC stack')

stackName = 'student-' + studentNumber

st = cf.create_stack(StackName = stackName,
                     TemplateBody = studentTemplate,
                     Parameters = [
                       { "ParameterKey": "KeyName", "ParameterValue": parms['keyName'] },
                       { "ParameterKey": "ControlInstanceType", "ParameterValue": controlNodeInstanceType },
                       { "ParameterKey": "ControlDiskSize", "ParameterValue": controlNodeDiskSize },
                       { "ParameterKey": "WorkerInstanceType", "ParameterValue": workerNodeInstanceType },
                       { "ParameterKey": "WorkerDiskSize", "ParameterValue": workerNodeDiskSize },
                       { "ParameterKey": "ImageId", "ParameterValue": studentNodeImageId },
                       { "ParameterKey": "SubnetNumber", "ParameterValue": studentNumber },
                       { "ParameterKey": "VpcId", "ParameterValue": parms['vpcId'] },
                       { "ParameterKey": "SecGroupAccess", "ParameterValue": parms['secGroupAccess'] },
                       { "ParameterKey": "RouteTable", "ParameterValue": parms['privateRouteTable'] }
                     ]
                     )

stwaiter = cf.get_waiter('stack_create_complete')

print('Waiting for stack creation to be complete...')

stwaiter.wait(StackName = stackName)

print('Stack creation complete')
