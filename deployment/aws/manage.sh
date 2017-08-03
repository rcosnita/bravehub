#!/usr/bin/env bash
set -eo pipefail

STACK_CONFIG_FILE=${1:-envs/stage.json}
STACK_ACTION=${2:-update-stack}

STACK_NAME=$(jq --raw-output .name ${STACK_CONFIG_FILE})
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
STACK_SWARM_MASTER_SPOT_PRICE=$(jq --raw-output .swarmMasterSpotPrice ${STACK_CONFIG_FILE})
STACK_SWARM_MASTER_CAPACITY_SPOT=$(jq --raw-output .swarmMasterCapacitySpot ${STACK_CONFIG_FILE})

STACK_SWARM_WORKER_INSTANCE_TYPE=$(jq --raw-output .swarmWorkerInstanceType ${STACK_CONFIG_FILE})
STACK_SWARM_WORKER_CAPACITY=$(jq --raw-output .swarmWorkerCapacity ${STACK_CONFIG_FILE})
STACK_SWARM_WORKER_SPOT_PRICE=$(jq --raw-output .swarmWorkerSpotPrice ${STACK_CONFIG_FILE})
STACK_SWARM_WORKER_CAPACITY_SPOT=$(jq --raw-output .swarmWorkerCapacitySpot ${STACK_CONFIG_FILE})


echo "Stack action: ${STACK_ACTION}"
echo "Stack name: ${STACK_NAME}"

STACK_PARAMS=(
  ParameterKey=StackName,ParameterValue=${STACK_NAME}
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
  ParameterKey=SwarmMasterSpotPrice,ParameterValue=${STACK_SWARM_MASTER_SPOT_PRICE}
  ParameterKey=SwarmMasterCapacitySpot,ParameterValue=${STACK_SWARM_MASTER_CAPACITY_SPOT}
  ParameterKey=SwarmWorkerInstanceType,ParameterValue=${STACK_SWARM_WORKER_INSTANCE_TYPE}
  ParameterKey=SwarmWorkerCapacity,ParameterValue=${STACK_SWARM_WORKER_CAPACITY}
  ParameterKey=SwarmWorkerSpotPrice,ParameterValue=${STACK_SWARM_WORKER_SPOT_PRICE}
  ParameterKey=SwarmWorkerCapacitySpot,ParameterValue=${STACK_SWARM_WORKER_CAPACITY_SPOT}
)

aws cloudformation ${STACK_ACTION} \
  --stack-name ${STACK_NAME} \
  --template-body file://$(pwd)/infra.yml \
  --parameters ${STACK_PARAMS[*]} \
  --capabilities CAPABILITY_IAM
