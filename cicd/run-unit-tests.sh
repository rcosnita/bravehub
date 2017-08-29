#!/usr/bin/env bash
set -eo pipefail

find . -name '__pycache__' | xargs rm -Rf

PROJECT_NAME=${1}
SOURCES=$(find ${PROJECT_NAME}/src -name 'test_*')
SOURCES+=$(find bravehub_shared -name 'test_*')

python3 -m unittest ${SOURCES[*]}
