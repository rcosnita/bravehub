#!/usr/bin/env bash
set -eo pipefail

. instance-descriptor.sh

export LC_ALL=C
sudo apt-get update -y
sudo apt-get install -y python-pip python-dev build-essential openssl libssl-dev awscli
sudo pip install --upgrade pip
sudo pip install virtualenv

mkdir provisioning
cd provisioning
aws s3 cp s3://${STACK_NAME}/provisioning/requirements.txt .
aws s3 cp --recursive s3://${STACK_NAME}/provisioning/roles roles/
aws s3 cp s3://${STACK_NAME}/provisioning/${ROLE}.yml .

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

ansible-playbook -i "localhost," -c local -v ${ROLE}.yml
