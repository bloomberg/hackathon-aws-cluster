#!/usr/bin/python

from __future__ import print_function
import boto3

region = 'eu-west-1'
project = 'gitsprint'
keyName = 'git1'
elasticIP = '34.252.213.213'
accessNodeInstanceType = 't2.xlarge'
accessNodeImageId = 'ami-de57fba7'
accessNodeAllowedIPs = '0.0.0.0/0'

ec2 = boto3.client(region_name = region, service_name = 'ec2')

allocationID = ec2.describe_addresses(Filters = [{'Name': 'public-ip', 'Values': [ elasticIP ] } ])['Addresses'][0]['AllocationId']

cf = boto3.client(region_name = region, service_name = 'cloudformation')

with open('git-vpc.json', 'r') as template_file:
    vpcTemplate = template_file.read()

print('Creating VPC stack')

st = cf.create_stack(StackName = 'git',
                     TemplateBody = vpcTemplate,
                     Capabilities = [ 'CAPABILITY_IAM' ],
                     Parameters = [
                       { "ParameterKey": "Project", "ParameterValue": project },
                       { "ParameterKey": "KeyName", "ParameterValue": keyName },
                       { "ParameterKey": "ElasticIp", "ParameterValue": allocationID },
                       { "ParameterKey": "AccessInboundCidrIp", "ParameterValue": accessNodeAllowedIPs },
                       { "ParameterKey": "AccessNodeImageId", "ParameterValue": accessNodeImageId },
                       { "ParameterKey": "AccessNodeInstanceType", "ParameterValue": accessNodeInstanceType }
                     ]
                     )

stwaiter = cf.get_waiter('stack_create_complete')

print('Waiting for stack creation to be complete...')

stwaiter.wait(StackName = 'git')

print('Stack creation complete')
