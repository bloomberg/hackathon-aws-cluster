#!/bin/sh -xe

REGION=eu-west-1
BUCKET=bbg-misc-eu

export AWS_DEFAULT_REGION=$REGION

aws s3 cp jepsen-vpc.json s3://$BUCKET
aws s3 cp jepsen-vpc-student.json s3://$BUCKET

aws cloudformation create-stack --stack-name jepsen --template-url https://s3-$REGION.amazonaws.com/$BUCKET/jepsen-vpc.json --parameters file://`pwd`/jepsen-vpc-parameters.json
