#!/bin/sh

aws cloudformation create-stack --stack-name student01 --template-body file:///Users/kpfleming/jepsen/jepsen-vpc-student.json --parameters file:///Users/kpfleming/jepsen/jepsen-vpc-student-parameters.json
