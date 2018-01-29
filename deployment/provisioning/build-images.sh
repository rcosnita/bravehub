#!/usr/bin/env bash
set -eo pipefail

ZOOKEEPER_VERSION=0.1.0
HBASE_VERSION=0.1.0
BRAVEHUB_VERSION=0.1.0

BRAVEHUB_CLOUD_ENV=${1}
BRAVEHUB_ENV=${2}
BRAVEHUB_REGISTRY_URI=${3}

WORKDIR=$(pwd)

rm -Rf images/*.tar

function login_to_aws {
  CLOUD_ENV=${1}
  local repository_uri=""

  case ${CLOUD_ENV} in
    aws)
      ecr_login=$(aws ecr get-login --no-include-email)
      eval ${ecr_login}
      ;;
    *)
      echo "Cloud environment ${CLOUD_ENV} is not supported."
      ;;
  esac
}

function create_repository {
  ROLE=${1}

  local repository_uri
  local repository_name=${BRAVEHUB_ENV}/${ROLE}

  aws ecr create-repository --repository-name ${repository_name} &> /dev/null || true
  repository_uri=$(aws ecr describe-repositories --repository-names ${repository_name} | \
                   jq -r .repositories[0].repositoryUri)
  echo ${repository_uri}
}

function upload_image {
  if [[ -z "${BRAVEHUB_REGISTRY_URI}" ]]; then
    return
  fi

  LOCAL_IMAGE=${1}
  ROLE=${2}
  VERSION=${3}

  REPOSITORY_URI=$(create_repository ${ROLE})
  IMAGE=${REPOSITORY_URI}:${VERSION}
  echo "Publishing ${LOCAL_IMAGE} to ${IMAGE}"
  docker tag ${LOCAL_IMAGE} ${IMAGE}
  docker push ${IMAGE}
}

if [[ ! -z "${BRAVEHUB_CLOUD_ENV}" ]]; then
  login_to_aws ${BRAVEHUB_CLOUD_ENV}
fi

ZOOKEEPER_IMAGE_NAME="bravehub/zookeeper:${ZOOKEEPER_VERSION}"
cd deployment/hadoop/zookeeper && docker build -t ${ZOOKEEPER_IMAGE_NAME} -f Dockerfile .
upload_image ${ZOOKEEPER_IMAGE_NAME} zookeeper ${ZOOKEEPER_VERSION}

cd ${WORKDIR}
HBASE_IMAGE_NAME="bravehub/hbase:${HBASE_VERSION}"
cd deployment/hadoop/hbase && docker build -t ${HBASE_IMAGE_NAME} -f Dockerfile .
upload_image ${HBASE_IMAGE_NAME} hbase ${HBASE_VERSION}

cd ${WORKDIR}
SETUP_DATABASE_IMAGE_NAME="bravehub/setup-database:${BRAVEHUB_VERSION}"
cd deployment/bravehub && docker build -t ${SETUP_DATABASE_IMAGE_NAME} -f Dockerfile .
upload_image ${SETUP_DATABASE_IMAGE_NAME} setup-database ${BRAVEHUB_VERSION}

cd ${WORKDIR}
CONFIGURATION_API_IMAGE_NAME="bravehub/configuration-api:${BRAVEHUB_VERSION}"
docker build -t ${CONFIGURATION_API_IMAGE_NAME} -f configuration-api/Dockerfile .
upload_image ${CONFIGURATION_API_IMAGE_NAME} configuration-api ${BRAVEHUB_VERSION}

cd ${WORKDIR}
CONFIGURATION_APP_IMAGE_NAME="bravehub/configuration-app:${BRAVEHUB_VERSION}"
docker-compose build configuration-app.api.internal.bravehub-dev.com && cd deploymentWORKDIR}
cd deployment/../configuration-app && docker build -t ${CONFIGURATION_APP_IMAGE_NAME} -f Dockerfile-prod .
upload_image ${CONFIGURATION_APP_IMAGE_NAME} configuration-app ${BRAVEHUB_VERSION}

cd ${WORKDIR}
PROVISIONING_API_IMAGE_NAME="bravehub/provisioning-api:${BRAVEHUB_VERSION}"
docker build -t ${PROVISIONING_API_IMAGE_NAME} -f provisioning-api/Dockerfile .
upload_image ${PROVISIONING_API_IMAGE_NAME} provisioning-api ${BRAVEHUB_VERSION}

cd ${WORKDIR}
ROUTER_IMAGE_NAME="bravehub/router:${BRAVEHUB_VERSION}"
cd deployment/../load-balancer && docker build -t ${ROUTER_IMAGE_NAME} -f Dockerfile .
upload_image ${ROUTER_IMAGE_NAME} router ${BRAVEHUB_VERSION}
