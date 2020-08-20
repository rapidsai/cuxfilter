#!/bin/bash
#
# Adopted from https://github.com/tmcdonell/travis-scripts/blob/dfaac280ac2082cd6bcaba3217428347899f2975/update-accelerate-buildbot.sh

set -e

export CUXFILTER_FILE=`conda build conda/recipes/cuxfilter --python=$PYTHON --output`

CUDA_REL=${CUDA_VERSION%.*}

if [ ${BUILD_MODE} != "branch" ]; then
  echo "Skipping upload"
  return 0
fi

if [ -z "$MY_UPLOAD_KEY" ]; then
    echo "No upload key"
    return 0
fi

if [ "$UPLOAD_CUXFILTER" == "1" ]; then
  LABEL_OPTION="--label main"
  echo "LABEL_OPTION=${LABEL_OPTION}"

  test -e ${CUXFILTER_FILE}
  echo "Upload cuXfilter"
  echo ${CUXFILTER_FILE}
  anaconda -t ${MY_UPLOAD_KEY} upload -u ${CONDA_USERNAME:-rapidsai} ${LABEL_OPTION} --skip-existing ${CUXFILTER_FILE}
fi
