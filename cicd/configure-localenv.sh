#!/usr/bin/env bash
set -eo pipefail

WORKDIR=$(pwd)

function create_venv {
  VENV_PATH=${1}
  SRC_PATH=${2}
  SHARED_PATH=${WORKDIR}/bravehub_shared

  pushd ${SRC_PATH}
  rm -Rf bravehub_shared
  ln -s ${SHARED_PATH} ${SRC_PATH}/bravehub_shared
  popd

  python3 -m venv ${VENV_PATH}
  . ${VENV_PATH}/bin/activate
  pip install -r requirements.txt
  pip install -r ${SRC_PATH}/bravehub_shared/requirements.txt
  pip install pylint
  deactivate
}

pushd bravehub_shared
echo "Configuring bravehub_shared"
create_venv $(pwd)/bravehub-shared-env $(pwd)
popd
pwd

pushd configuration-api
echo "Configuring configuration-api"
create_venv $(pwd)/configuration-api-env $(pwd)/src
popd

pushd logging-api
echo "Configuring logging-api"
create_venv $(pwd)/logging-api-env $(pwd)/src
popd

pushd provisioning-api
echo "Configuring provisioning-api"
create_venv $(pwd)/provisioning-api-env $(pwd)/src
popd

pushd scenegraph-api
echo "Configuring scenegraph-api"
create_venv $(pwd)/scenegraph-api-env $(pwd)/src
popd

pushd identity-api
echo "Configuring identity-api"
create_venv $(pwd)/identity-api-env $(pwd)/src
popd
