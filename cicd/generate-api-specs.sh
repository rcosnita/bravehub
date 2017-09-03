#!/usr/bin/env bash
set -eo pipefail

OUTPUT_FOLDER=dist/apis
DOCS_LOCATION=docs/specs/apis

rm -Rf ${OUTPUT_FOLDER}
mkdir -p ${OUTPUT_FOLDER}/${DOCS_LOCATION}
find ${DOCS_LOCATION} -name '*.apib' | xargs -I{} node_modules/.bin/aglio --theme-template triple \
    -o ${OUTPUT_FOLDER}/{}.html \
    -i {}

mv ${OUTPUT_FOLDER}/${DOCS_LOCATION}/*.apib.html ${OUTPUT_FOLDER}
rm -Rf ${OUTPUT_FOLDER}/docs
