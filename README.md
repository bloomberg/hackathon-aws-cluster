# git-hackathon-vpc

This repository contains Python scripts and CloudFormation templates used to launch a cluster of user instances for a Git hackathon. The Python scripts
require Python 3 and the 'boto3' module (install with 'pip' or any other mechanism you like).

## Setup

You will need an AWS access key (both "access key id" and "secret access key") with sufficient privileges in the region you wish to use in order to create a variety of AWS objects. These credentials
should be set as environment variables ```AWS_ACCESS_KEY_ID``` and ```AWS_SECRET_ACCESS_KEY```.

## git-vpc.json

This is the 'outer' CloudFormation template; it creates the VPC, an access node on a preselected ElasticIP, various other resources, and configures the access node to provide HTTP reverse-proxy access into the user machines.

## git-vpc-user.json

This is the 'inner' CloudFormation template; it creates an instance in an isolated VPC subnet and sets up everything necessary on the instance.
This includes generating a random password for the 'ubuntu' user (which is copied into a private S3 bucket created by the 'outer' template) and
ShellInABox setup so that the proxy on the 'outer' node can provide access to the instance.

## launch-vpc.py

Script which launches the 'outer' CloudFormation stack. There are some configuration parameters at the top of the script.

## launch-vpc-user.py

Script which launches one (or more) user CloudFormation stacks. This accepts one or two command line parameters, indicating the user numbers of the
stacks to be launched. There are some configuration parameters at the top of the script, and the script also obtains information left in 'outputs' in the
'outer' stack.

## get-passwords.py

Retrieves the randomly-generated 'ubuntu' passwords for all user instances in the stack, putting them into a 'passwords' subdirectory.

## cleanup.py

Destroys all the resources currently running, starting with the user stacks and ending with the 'outer' stack.

## index.html and proxies.conf

Files installed into the access node to setup reverse-proxies in the Apache HTTPD running there.

## Access

Once the stacks are launched, users can connect to the IP address at the top of the ```launch-vpc.py``` script with any browser. They will be presented a list of links
to the user instances; clicking a link will open a new tab (or window) in their browser, and they will be presented with a login prompt. They can login as ```ubuntu```
using the randomly-generated password obtained by running the ```get-passwords.py``` script; if this has been emailed to them, they can copy-and-paste it but *MUST*
use the Edit/Paste menu in their browser (or similar menu item if their browser calls it something different) as the ShellInABox window will intercept all normal
'paste' keystrokes and send them to the VM, so they will not be handled locally in the browser.

Once logged in the users will find a clone of https://github.com/git/git in the `git` directory. All dependencies to build it, and its tests and documentation, have
been installed. In addition many common text editors (Emacs, Vim, Nano) are installed and various other tools. Users have ```sudo``` access and can install any
additional packages they find necessary or useful. ```USE_LIBPCRE``` has been set in ```.bash_profile``` so that Git will be built with PCRE support.

## Typical workflow

1. Clone this repository/branch.
2. Set AWS access key environment variables.
3. Run ```launch-vpc.py``` and wait for it to finish.
4. Run ```launch-vpc-user.py <x> <y>``` where 'x' and 'y' define the starting and ending 'user numbers' to be launched. If 'y' is not supplied, only a single user number will be launched.
Wait for it finish.
5. Run ```get-passwords.py```. Copy the ```passwords.txt``` file from the ```passwords``` directory somewhere that you can use it to email the passwords to the users.
6. Run ```cleanup.py``` to destroy everything when the event is complete.

If any user instance needs to be destroyed and recreated, you will need to log in to the AWS console, navigate to the CloudFormation service, and then delete that user's stack before
attempting to recreate it. You will need to be sure to select the proper AWS region (using the drop-down selector in the top-right corner) in the console in order to
see the resources created by CloudFormation.

## Configuration

The user instances are quad-core VMs with 8GB of RAM, so parallel builds should work quite well.

## AMI Notes

The image for the access node needs the CloudFormation tools and Apache HTTPD with mod_proxy and mod_proxy_http enabled. The cloud-init script in the CloudFormation template
expects the Debian/Ubuntu layout of configuration files for the web server.

The image for the user nodes needs the CloudFormation tools, the AWS CLI tool, and ShellInABox. SIAB must be configured to listen on port 80 with SSL disabled (and the SSL menu item disabled).
