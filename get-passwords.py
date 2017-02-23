#!/usr/bin/python

from __future__ import print_function
import sys
import os
import boto3

region = 'us-east-1'

cf = boto3.client(region_name = region, service_name = 'cloudformation')

st = cf.describe_stacks(StackName = 'coa')

outputs = st['Stacks'][0]['Outputs']

for out in outputs:
    if out['Description'] == 'Bucket':
        bucket = out['OutputValue']

s3 = boto3.client(region_name = region, service_name = 's3')

list = s3.list_objects_v2(Bucket = bucket, Prefix = 'passwd.')

if not os.path.exists('passwords'):
    os.makedirs('passwords')

for obj in list['Contents']:
    print("Getting", obj['Key'])
    with open('passwords/' + obj['Key'] + '.txt', 'w') as pwfile:
        s3.download_fileobj(bucket, obj['Key'], pwfile)
