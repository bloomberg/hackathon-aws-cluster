#!/usr/bin/env python3

import sys
import os
import boto3
import io
import csv

region = 'eu-west-1'

cf = boto3.client(region_name = region, service_name = 'cloudformation')

st = cf.describe_stacks(StackName = 'git')

outputs = st['Stacks'][0]['Outputs']

for out in outputs:
    if out['Description'] == 'Bucket':
        bucket = out['OutputValue']

s3 = boto3.client(region_name = region, service_name = 's3')

list = s3.list_objects_v2(Bucket = bucket, Prefix = 'passwd.')

if not os.path.exists('passwords'):
    os.makedirs('passwords')

passwords = []

for obj in list['Contents']:
    print("Getting", obj['Key'])
    passwd = io.BytesIO()
    s3.download_fileobj(bucket, obj['Key'], passwd)

    with open('passwords/' + obj['Key'] + '.txt', 'wb') as pwfile:
        pwfile.write(passwd.getvalue())

    passwords.append([obj['Key'][7:], passwd.getvalue().strip()])

passwords.sort(key = lambda x: int(x[0]))
with open('passwords/passwords.csv', 'w') as pwfile:
    csv.writer(pwfile).writerows(passwords)
