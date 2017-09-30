#!/usr/bin/env bash
set -eo pipefail

PROJECT_NAME=${1}
WORKDIR=$(pwd)

if [[ "${PROJECT_NAME}" != "load-balancer" ]]; then
  pylint bravehub_shared ${PROJECT_NAME}/src
else
  cd load-balancer
  LINT_SRC=$(find src -iname src/build -name "*.cpp" -o -name "*.h")

  # python third-party/depot_tools/cpplint.py --linelength=120 ${LINT_SRC[*]}

  cd ${WORKDIR}
  docker build -t bravehub/cppcoreguidelines -f cicd/docker/Dockerfile-cppcoreguidelines cicd/docker
  docker run --rm \
    --env CPP_LINTING_PATH=/root/load-balancer/src \
    -v $(pwd)/load-balancer/src:/root/load-balancer/src \
    -v $(pwd)/load-balancer/third-party:/root/load-balancer/third-party \
    --workdir /root/load-balancer \
    bravehub/cppcoreguidelines
fi

cd ${WORKDIR}
