#!/usr/bin/env bash
set -eo pipefail

if [ "$(uname)" = "Darwin" ]; then
    echo "Using clang-format for Darwin"
    CLANG_PATH=third-party/clang-format/bin/darwin_x64/clang-format
else
    echo "Using clang-format for Linux"
    CLANG_PATH=third-party/clang-format/bin/linux_x64/clang-format
fi

function diffFiles() {
    curr_file=$1
    new_file=$2.new
    ${CLANG_PATH} ${curr_file} >> ${new_file}

    diffs=`diff ${curr_file} ${new_file}`
    rm -f ${new_file}

    if [[ !  -z  ${diffs} ]]; then
        echo "Please format file ${curr_file}. You can use cicd/format-all-code.sh"
        echo "See the differences below: "
        echo ${diffs}
        exit 1
    fi
}

function formatFile() {
    curr_file=$1
    curr_content=`cat ${curr_file}`
    ${CLANG_PATH} -i ${curr_file}
    new_content=`cat ${curr_file}`

    file_altered=0
    if [ "${curr_content}" != "${new_content}" ]; then
        echo "File ${curr_file} formatted"
        file_altered=1
    fi
}

affected_files=0
rm -f .search-index
find src -name '*.*' -iname src/build -print0 >> .search-index
# find tests/unit -name '*.*' -print0 >> .search-index

while IFS=  read -r -d $'\0' filename; do
    if [ "${RUNNING_ENV}" = "cicd" ]; then
        diffFiles "${filename}" "${filename}.new"
    else
        formatFile "${filename}"
        if [ ${file_altered} == 1 ]; then
            affected_files=${affected_files+1}
        fi
    fi
done <.search-index
rm -f .search-index

if [ $affected_files -gt 0 ]; then
    exit 1
fi
