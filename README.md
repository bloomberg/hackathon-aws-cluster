# jepsen-training-vpc

This repository contains Python scripts and CloudFormation templates used to launch a cluster of student training instances for Jepsen classes.

## jepsen-vpc.json

This is the 'outer' CloudFormation template; it creates the VPC, an access node on a preselected ElasticIP, various other resources, and configures the access node tto provide HTTP reverse-proxy access into the student clusters.

## jepsen-vpc-student.json

This is the 'inner' CloudFormation template; it creates six instances (one 'control' and five 'worker' nodes) and sets up everything necessary on the instances.
This includes generating a random password for the 'admin' user (which is copied into a private S3 bucket created by the 'outer' template), an SSH keypair used
for connections between instances in the student cluster (also copied into the S3 bucket), installing ShellInABox on the control node so that the student
can reach it via web browser (through the reverse proxy on the access node), and ensuring that the Jepsen 'rescan-nodes' script is run on each 'admin' login.

## launch-vpc.py

Script which launches the 'outer' CloudFormation stack. There are some configuration parameters at the top of the script.

## launch-vpc-student.py

Script which launches one (or more) student CloudFormation stacks. This accepts one or two command line parameters, indicating the student numbers of the
stacks to be launched. There are some configuration parameters at the top of the script, and the script also obtains information left in 'outputs' in the
'outer' stack.

## get-passwords.py

Retrieves the randomly-generated 'admin' passwords for all student clusters in the stack, putting them into a 'passwords' subdirectory.

## cleanup.py

Destroys all the resources currently running, starting with the student stacks and ending with the 'outer' stack.

## index.html and proxies.conf

Files installed into the access node to setup reverse-proxies in the Apache HTTPD running there.
