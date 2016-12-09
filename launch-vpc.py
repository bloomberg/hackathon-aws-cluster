#!/usr/bin/python

from __future__ import print_function
import boto3

region = 'eu-west-1'
keyName = 'jtest1'
elasticIP = '52.213.115.56'
accessNodeInstanceType = 't2.xlarge'
accessNodeImageId = 'ami-7d45150e'
accessNodeAllowedIPs = '0.0.0.0/0'

ec2 = boto3.client(region_name = region, service_name = 'ec2')

allocationID = ec2.describe_addresses(Filters = [{'Name': 'public-ip', 'Values': [ elasticIP ] } ])['Addresses'][0]['AllocationId']

cf = boto3.client(region_name = region, service_name = 'cloudformation')

with open('jepsen-vpc.json', 'r') as template_file:
    vpcTemplate = template_file.read()

print('Creating VPC stack')

st = cf.create_stack(StackName = 'jepsen',
                     TemplateBody = vpcTemplate,
                     Capabilities = [ 'CAPABILITY_IAM' ],
                     Parameters = [
                       { "ParameterKey": "KeyName", "ParameterValue": keyName },
                       { "ParameterKey": "ElasticIp", "ParameterValue": allocationID },
                       { "ParameterKey": "AccessInboundCidrIp", "ParameterValue": accessNodeAllowedIPs },
                       { "ParameterKey": "AccessNodeImageId", "ParameterValue": accessNodeImageId }
                       { "ParameterKey": "AccessNodeInstanceType", "ParameterValue": accessNodeInstanceType }
                     ]
                     )

stwaiter = cf.get_waiter('stack_create_complete')

print('Waiting for stack creation to be complete...')

stwaiter.wait(StackName = 'jepsen')

print('Stack creation complete')
