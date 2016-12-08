#!/usr/bin/python

from __future__ import print_function
import json
import boto3

region = 'eu-west-1'
keyName = 'jtest1'
elasticIP = '52.213.115.56'
accessNodeInstanceType = 't2.xlarge'
accessNodeImageId = 'ami-9398d3e0'
accessNodeAllowedIPs = '0.0.0.0/0'

ec2 = boto3.client(region_name = region, service_name = 'ec2')

allocationID = ec2.describe_addresses(Filters = [{'Name': 'public-ip', 'Values': [ elasticIP ] } ])['Addresses'][0]['AllocationId']

cf = boto3.client(region_name = region, service_name = 'cloudformation')

with open('jepsen-vpc.json', 'r') as template_file:
    vpcTemplate = template_file.read()

print('Creating VPC stack')

st = cf.create_stack(StackName = 'jepsen',
                     TemplateBody = vpcTemplate,
                     Parameters = [
                       { "ParameterKey": "KeyName", "ParameterValue": keyName },
                       { "ParameterKey": "ElasticIp", "ParameterValue": allocationID },
                       { "ParameterKey": "AccessInboundCidrIp", "ParameterValue": accessNodeAllowedIPs },
                       { "ParameterKey": "AccessNodeImageId", "ParameterValue": accessNodeImageId }
                     ]
                     )

stwaiter = cf.get_waiter('stack_create_complete')

print('Waiting for stack creation to be complete...')

stwaiter.wait(StackName = 'jepsen')

print('Stack creation complete')

st = cf.describe_stacks(StackName = 'jepsen')

outputs = st['Stacks'][0]['Outputs']

print(outputs)

for out in outputs:
    if out['Description'] == 'PrivateRouteTable':
        privateRouteTable = out['OutputValue']
    elif out['Description'] == 'VpcId':
        vpcId = out['OutputValue']
    elif out['Description'] == 'SecGroupAccess':
        secGroupAccess = out['OutputValue']

with open('jepsen-vpc.tmp', 'w') as output_file:
    output_file.write(json.dumps({"privateRouteTable": privateRouteTable,
                                  "vpcId": vpcId,
                                  "secGroupAccess": secGroupAccess,
                                  "keyName": keyName,
                                  "region": region
                                 }))
    output_file.write('\n')

print('Parameters saved in jepsen-vpc.tmp, student clusters can be launched with launch-vpc-student.py')
