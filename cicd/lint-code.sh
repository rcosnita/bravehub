#!/usr/bin/env bash
set -eo pipefail

PROJECT_NAME=${1}
pylint bravehub_shared ${PROJECT_NAME}/src
