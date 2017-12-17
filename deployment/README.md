Below you can find the high level diagram as well as required access for Bravehub platform.

![Deployment topology](../docs/images/deployment/deployment-topology.png)

## Getting started

### AWS

A **Bravehub** stack requires a key pair named the same as the stack. This keypair must be created before trying to spin up a new stack.

#### Create a new stack

```bash
export AWS_DEFAULT_REGION=eu-west-1 # replace this with the desired region
export AWS_DEFAULT_PROFILE=bravehub-stage # replace this with your actual profile

WORKDIR=$(pwd)
cd deployment/provisioning && sh build-images.sh aws stage 083512914311.dkr.ecr.eu-west-1.amazonaws.com

cd ${WORKDIR}/deployment/aws
sh manage.sh envs/stage.json create-stack
```

#### Update an existing stack

```bash
export AWS_DEFAULT_REGION=eu-west-1 # replace this with the desired region
export AWS_DEFAULT_PROFILE=bravehub-stage # replace this with your actual profile

WORKDIR=$(pwd)
cd deployment/provisioning && sh build-images.sh aws stage 083512914311.dkr.ecr.eu-west-1.amazonaws.com

cd ${WORKDIR}/deployment/aws
sh manage.sh envs/stage.json
```

The json file contains all the attributes required to configure Bravehub infrastructure.

By default, we don't grant ssh access from the internet to our infrastructure. In very special cases, **admins** can modify **router-sg** security group in order to gain ssh access.
Whenever they do this they must be very strict with the source of the request: **theirip/32**.
!!!!! Do not use open to the world rules like **0.0.0.0/0**.

### Provisioning

* [Provisioning how to](provisioning/README.md)
