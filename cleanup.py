#!/usr/bin/python

from __future__ import print_function
import sys
import boto3
import concurrent.futures
import shutil

region = 'eu-west-1'

cf = boto3.client(region_name = region, service_name = 'cloudformation')

st = cf.describe_stacks(StackName = 'git')

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
        print("Deleting", obj['Key'])
        s3.delete_object(Bucket = bucket, Key = obj['Key'])
        waiter.wait(Bucket = bucket, Key = obj['Key'])

stacks = cf.list_stacks(StackStatusFilter = [ 'CREATE_IN_PROGRESS',
                                              'CREATE_FAILED',
                                              'CREATE_COMPLETE',
                                              'ROLLBACK_IN_PROGRESS',
                                              'ROLLBACK_FAILED',
                                              'ROLLBACK_COMPLETE'
                                            ])


def delete_user(stackName):
    print("Deleting", stackName)
    cf.delete_stack(StackName = stackName)
    waiter = cf.get_waiter('stack_delete_complete')
    return (stackName, waiter)

def wait_on_stack(t):
    t[1].wait(StackName = t[0])
    print("Stack", t[0], "deleted")

print("Deleting user stacks")
with concurrent.futures.ThreadPoolExecutor(max_workers = len(stacks['StackSummaries'])) as executor:
    fs = { executor.submit(wait_on_stack, delete_user(x['StackName'])) for x in stacks['StackSummaries'] if x['StackName'].startswith('user-') }
    print('Waiting for stack deletion to be complete...')
    concurrent.futures.wait(fs)

print("Deleting top-level stack")
cf.delete_stack(StackName = 'git')
waiter = cf.get_waiter('stack_delete_complete')
waiter.wait(StackName = 'git')

shutil.rmtree('passwords')
