#!/usr/bin/python

from __future__ import print_function
import boto3

region = 'us-east-1'
keyName = 'coa1'
elasticIP = '34.200.191.76'
accessNodeInstanceType = 't2.xlarge'
accessNodeImageId = 'ami-b14ba7a7'
accessNodeAllowedIPs = '0.0.0.0/0'

ec2 = boto3.client(region_name = region, service_name = 'ec2')

allocationID = ec2.describe_addresses(Filters = [{'Name': 'public-ip', 'Values': [ elasticIP ] } ])['Addresses'][0]['AllocationId']

cf = boto3.client(region_name = region, service_name = 'cloudformation')

with open('coa-vpc.json', 'r') as template_file:
    vpcTemplate = template_file.read()

print('Creating VPC stack')

st = cf.create_stack(StackName = 'coa',
                     TemplateBody = vpcTemplate,
                     Capabilities = [ 'CAPABILITY_IAM' ],
                     Parameters = [
                       { "ParameterKey": "KeyName", "ParameterValue": keyName },
                       { "ParameterKey": "ElasticIp", "ParameterValue": allocationID },
                       { "ParameterKey": "AccessInboundCidrIp", "ParameterValue": accessNodeAllowedIPs },
                       { "ParameterKey": "AccessNodeImageId", "ParameterValue": accessNodeImageId },
                       { "ParameterKey": "AccessNodeInstanceType", "ParameterValue": accessNodeInstanceType }
                     ]
                     )

stwaiter = cf.get_waiter('stack_create_complete')

print('Waiting for stack creation to be complete...')

stwaiter.wait(StackName = 'coa')

print('Stack creation complete')
