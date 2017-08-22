#!/usr/bin/env bash
set -eo pipefail

ZOOKEEPER_VERSION=0.1.0
HBASE_VERSION=0.1.0
BRAVEHUB_VERSION=0.1.0

WORKDIR=$(pwd)

rm -Rf images/*.tar

ZOOKEEPER_IMAGE_NAME="bravehub/zookeeper:${ZOOKEEPER_VERSION}"
cd ../hadoop/zookeeper && docker build -t ${ZOOKEEPER_IMAGE_NAME} -f Dockerfile .
docker save ${ZOOKEEPER_IMAGE_NAME} -o ${WORKDIR}/images/zookeeper-${ZOOKEEPER_VERSION}.tar

cd ${WORKDIR}
HBASE_IMAGE_NAME="bravehub/hbase:${HBASE_VERSION}"
cd ../hadoop/hbase && docker build -t ${HBASE_IMAGE_NAME} -f Dockerfile .
docker save ${HBASE_IMAGE_NAME} -o ${WORKDIR}/images/hbase-${HBASE_VERSION}.tar

cd ${WORKDIR}
SETUP_DATABASE_IMAGE_NAME="bravehub/setup-database:${BRAVEHUB_VERSION}"
cd ../bravehub && docker build -t ${SETUP_DATABASE_IMAGE_NAME} -f Dockerfile .
docker save ${SETUP_DATABASE_IMAGE_NAME} -o ${WORKDIR}/images/setup-database-${BRAVEHUB_VERSION}.tar
