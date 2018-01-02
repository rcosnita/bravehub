#!/usr/bin/env bash
set -eo pipefail

find . -name '__pycache__' | xargs rm -Rf

PROJECT_NAME=${1}

if [[ ${PROJECT_NAME} == "bravehub_shared" ]]; then
  SOURCES=$(find ${PROJECT_NAME}/tests -name 'test_*.py')
else
  SOURCES=$(find ${PROJECT_NAME}/src/tests -name 'test_*.py')
fi

python3 -m unittest ${SOURCES[*]}
