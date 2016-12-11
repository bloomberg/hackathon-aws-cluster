#!/usr/bin/python

from __future__ import print_function
import sys
import boto3

region = 'eu-west-1'

cf = boto3.client(region_name = region, service_name = 'cloudformation')

st = cf.describe_stacks(StackName = 'jepsen')

outputs = st['Stacks'][0]['Outputs']

for out in outputs:
    if out['Description'] == 'Bucket':
        bucket = out['OutputValue']

s3 = boto3.client(region_name = region, service_name = 's3')

list = s3.list_objects_v2(Bucket = bucket)

waiter = s3.get_waiter('object_not_exists')

print("Clearing contents of S3 bucket", bucket)
if 'Contents' in list:
    for obj in list['Contents']:
        print("Deleting ", obj['Key'])
        s3.delete_object(Bucket = bucket, Key = obj['Key'])
        waiter.wait(Bucket = bucket, Key = obj['Key'])

stacks = cf.list_stacks(StackStatusFilter = [ 'CREATE_IN_PROGRESS',
                                              'CREATE_FAILED',
                                              'CREATE_COMPLETE',
                                              'ROLLBACK_IN_PROGRESS',
                                              'ROLLBACK_FAILED',
                                              'ROLLBACK_COMPLETE'
                                            ])

waiter = cf.get_waiter('stack_delete_complete')

print("Deleting student stacks")
for stack in stacks['StackSummaries']:
    if stack['StackName'].startswith('student-'):
        print("Deleting", stack['StackName'])
        cf.delete_stack(StackName = stack['StackName'])
        waiter.wait(StackName = stack['StackName'])

print("Deleting top-level stack")
cf.delete_stack(StackName = 'jepsen')
waiter.wait(StackName = 'jepsen')
