#!/bin/sh

aws cloudformation create-stack --stack-name jepsen --template-body file:///Users/kpfleming/jepsen/jepsen-vpc-solo.json --parameters file:///Users/kpfleming/jepsen/jepsen-vpc-solo-parameters.json
