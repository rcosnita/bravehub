#!/usr/bin/env bash
set -eo pipefail

STACK_CONFIG_FILE=${1:-envs/stage.json}
STACK_CFN_S3=${2:-bravehub-bootstrap-files-cfn}
STACK_ACTION=${3:-update-stack}
STACK_WAIT_ACTION=stack-update-complete

if [[ ${STACK_ACTION} == "create-stack" ]]; then
  STACK_WAIT_ACTION=stack-create-complete
fi

STACK_NAME=$(jq --raw-output .name ${STACK_CONFIG_FILE})
STACK_DNS_SUFFIX=$(jq --raw-output .dnsSuffix ${STACK_CONFIG_FILE})
STACK_ENV=$(jq --raw-output .env ${STACK_CONFIG_FILE})
STACK_CIDR_PREFIX=$(jq --raw-output .cidrPrefix ${STACK_CONFIG_FILE})

STACK_ROUTER_INSTANCE_TYPE=$(jq --raw-output .routerInstanceType ${STACK_CONFIG_FILE})
STACK_ROUTER_MIN_CAPACITY=$(jq --raw-output .routerMinCapacity ${STACK_CONFIG_FILE})
STACK_ROUTER_MAX_CAPACITY=$(jq --raw-output .routerMaxCapacity ${STACK_CONFIG_FILE})
STACK_ROUTER_DESIRED_CAPACITY=$(jq --raw-output .routerDesiredCapacity ${STACK_CONFIG_FILE})
STACK_ROUTER_SPOT_PRICE=$(jq --raw-output .routerSpotPrice ${STACK_CONFIG_FILE})
STACK_ROUTER_INSTANCE_TYPE_SPOT=$(jq --raw-output .routerInstanceTypeSpot ${STACK_CONFIG_FILE})
STACK_ROUTER_MIN_CAPACITY_SPOT=$(jq --raw-output .routerMinCapacitySpot ${STACK_CONFIG_FILE})
STACK_ROUTER_MAX_CAPACITY_SPOT=$(jq --raw-output .routerMaxCapacitySpot ${STACK_CONFIG_FILE})
STACK_ROUTER_DESIRED_CAPACITY_SPOT=$(jq --raw-output .routerDesiredCapacitySpot ${STACK_CONFIG_FILE})

STACK_SWARM_MASTER_INSTANCE_TYPE=$(jq --raw-output .swarmMasterInstanceType ${STACK_CONFIG_FILE})
STACK_SWARM_MASTER_CAPACITY=$(jq --raw-output .swarmMasterCapacity ${STACK_CONFIG_FILE})

STACK_SWARM_WORKER_INSTANCE_TYPE=$(jq --raw-output .swarmWorkerInstanceType ${STACK_CONFIG_FILE})
STACK_SWARM_WORKER_CAPACITY=$(jq --raw-output .swarmWorkerCapacity ${STACK_CONFIG_FILE})
STACK_SWARM_WORKER_SPOT_PRICE=$(jq --raw-output .swarmWorkerSpotPrice ${STACK_CONFIG_FILE})
STACK_SWARM_WORKER_CAPACITY_SPOT=$(jq --raw-output .swarmWorkerCapacitySpot ${STACK_CONFIG_FILE})

STACK_DOCKER_REGISTRY=$(jq --raw-output .dockerRegistry ${STACK_CONFIG_FILE})
STACK_DOCKER_REGISTRY_ARN=$(jq --raw-output .dockerRegistryArn ${STACK_CONFIG_FILE})
STACK_DOCKER_REGISTRY_ID=$(jq --raw-output .dockerRegistryId ${STACK_CONFIG_FILE})

function create_stack {
  echo "Stack action: ${STACK_ACTION}"
  echo "Stack name: ${STACK_NAME}"

  STACK_PARAMS=(
    ParameterKey=StackName,ParameterValue=${STACK_NAME}
    ParameterKey=DnsSuffix,ParameterValue=${STACK_DNS_SUFFIX}
    ParameterKey=BravehubEnv,ParameterValue=${STACK_ENV}
    ParameterKey=StackCidrPrefix,ParameterValue=${STACK_CIDR_PREFIX}
    ParameterKey=RouterInstanceType,ParameterValue=${STACK_ROUTER_INSTANCE_TYPE}
    ParameterKey=RouterMinCapacity,ParameterValue=${STACK_ROUTER_MIN_CAPACITY}
    ParameterKey=RouterMaxCapacity,ParameterValue=${STACK_ROUTER_MAX_CAPACITY}
    ParameterKey=RouterDesiredCapacity,ParameterValue=${STACK_ROUTER_DESIRED_CAPACITY}
    ParameterKey=RouterInstanceSpotPrice,ParameterValue=${STACK_ROUTER_SPOT_PRICE}
    ParameterKey=RouterInstanceTypeSpot,ParameterValue=${STACK_ROUTER_INSTANCE_TYPE_SPOT}
    ParameterKey=RouterMinCapacitySpot,ParameterValue=${STACK_ROUTER_MIN_CAPACITY_SPOT}
    ParameterKey=RouterMaxCapacitySpot,ParameterValue=${STACK_ROUTER_MAX_CAPACITY_SPOT}
    ParameterKey=RouterDesiredCapacitySpot,ParameterValue=${STACK_ROUTER_DESIRED_CAPACITY_SPOT}
    ParameterKey=SwarmMasterInstanceType,ParameterValue=${STACK_SWARM_MASTER_INSTANCE_TYPE}
    ParameterKey=SwarmMasterCapacity,ParameterValue=${STACK_SWARM_MASTER_CAPACITY}
    ParameterKey=SwarmWorkerInstanceType,ParameterValue=${STACK_SWARM_WORKER_INSTANCE_TYPE}
    ParameterKey=SwarmWorkerCapacity,ParameterValue=${STACK_SWARM_WORKER_CAPACITY}
    ParameterKey=SwarmWorkerSpotPrice,ParameterValue=${STACK_SWARM_WORKER_SPOT_PRICE}
    ParameterKey=SwarmWorkerCapacitySpot,ParameterValue=${STACK_SWARM_WORKER_CAPACITY_SPOT}
    ParameterKey=StackDockerRegistry,ParameterValue=${STACK_DOCKER_REGISTRY}
    ParameterKey=StackDockerRegistryArn,ParameterValue=${STACK_DOCKER_REGISTRY_ARN}
    ParameterKey=StackDockerRegistryId,ParameterValue=${STACK_DOCKER_REGISTRY_ID}
  )

  CFN_FILE=s3://${STACK_CFN_S3}/${STACK_ENV}/infra.yml
  CFN_TPL_PATH=https://s3-${AWS_DEFAULT_REGION}.amazonaws.com/${STACK_CFN_S3}/${STACK_ENV}/infra.yml
  aws s3 cp infra.yml ${CFN_FILE}

  aws cloudformation ${STACK_ACTION} \
    --stack-name ${STACK_NAME} \
    --template-url ${CFN_TPL_PATH} \
    --parameters ${STACK_PARAMS[*]} \
    --capabilities CAPABILITY_IAM \

  aws cloudformation wait ${STACK_WAIT_ACTION} \
    --stack-name ${STACK_NAME}
}

function publish_docker_images {
  echo "Publish the docker images to ${STACK_DOCKER_REGISTRY}."
  WORKDIR=$(pwd)
  
  cd ../provisioning && \
    sh build-images.sh aws ${STACK_ENV} ${STACK_DOCKER_REGISTRY}

  cd ${WORKDIR}
}

publish_docker_images
create_stack
