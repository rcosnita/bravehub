#!/usr/bin/env bash
set -eo pipefail

. instance-descriptor.sh

export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo dpkg-reconfigure -f noninteractive locales
sudo apt-get update -y
sudo apt-get install -y python-pip python-dev python3-pip python3-dev python3-venv python3-apt build-essential openssl libssl-dev awscli

rm -Rf provisioning
mkdir provisioning
cd provisioning
aws s3 cp s3://${STACK_NAME}/provisioning/requirements.txt .
aws s3 cp --recursive s3://${STACK_NAME}/provisioning/images images/
aws s3 cp --recursive s3://${STACK_NAME}/provisioning/inventory inventory/
aws s3 cp --recursive s3://${STACK_NAME}/provisioning/roles roles/
aws s3 cp s3://${STACK_NAME}/provisioning/${ROLE}.yml .

sudo pip install --upgrade pip
sudo pip3 install --upgrade pip
sudo pip install --upgrade awscli
sudo pip3 install --upgrade awscli

python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
cp -R /usr/lib/python3/dist-packages/apt* venv/lib/python3.*/site-packages/
pip install -r requirements.txt

ansible-playbook -i inventory/local -v -e "ansible_python_interpreter=$(pwd)/venv/bin/python3" ${ROLE}.yml
