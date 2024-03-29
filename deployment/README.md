Below you can find the high level diagram as well as required access for Bravehub platform.

![Deployment topology](../docs/images/deployment/deployment-topology.png)

## Getting started

### AWS

![Deployment AWS CFN](../docs/images/deployment/deployment-aws-cfn.png)

A **Bravehub** stack requires:

* a key pair named the same as the stack. This keypair must be created before trying to spin up a new stack.
* a S3 bucket where cloudformation stack files can be published.
* an ECS registry where images can be pushed / pulled. It must be created under the same account where the cluster is going to be created. 

#### Create a new stack

```bash
export AWS_DEFAULT_REGION=eu-west-1 # replace this with the desired region
export AWS_DEFAULT_PROFILE=bravehub-stage # replace this with your actual profile

cd ${WORKDIR}/deployment/aws
sh manage.sh envs/stage.json bravehub-bootstrap-files-cfn create-stack # replace bravehub-bootstrap-files-cfn with the actual s3 bucket where cfn files are published.
```

#### Update an existing stack

```bash
export AWS_DEFAULT_REGION=eu-west-1 # replace this with the desired region
export AWS_DEFAULT_PROFILE=bravehub-stage # replace this with your actual profile

cd ${WORKDIR}/deployment/aws
sh manage.sh envs/stage.json bravehub-bootstrap-files-cfn # replace bravehub-bootstrap-files-cfn with the actual s3 bucket where cfn files are published.
```

The json file contains all the attributes required to configure Bravehub infrastructure.

By default, we don't grant ssh access from the internet to our infrastructure. In very special cases, **admins** can modify the **BastionSecurityGroup** for gaining ssh access.
Whenever they do this they must be very strict with the source of the request: **theirip/32**.
!!!!! Do not use open to the world rules like **0.0.0.0/0**.

### Provisioning

* [Provisioning how to](provisioning/README.md)
