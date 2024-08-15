#!/bin/bash
# Copyright (c) 2023, NVIDIA CORPORATION.

set -e

rapids-logger "Create test_external conda environment"
. /opt/conda/etc/profile.d/conda.sh

# Install external dependencies into test_external conda environment
rapids-dependency-file-generator \
  --output conda \
  --file-key test_external \
  --matrix "cuda=${RAPIDS_CUDA_VERSION%.*};arch=$(arch);py=${RAPIDS_PY_VERSION}" | tee env.yaml

rapids-mamba-retry env create --yes -f env.yaml -n test_external

# Temporarily allow unbound variables for conda activation.
set +u
conda activate test_external
set -u

rapids-print-env

# Define input parameter
PROJECT="${1:-all}"
PR_NUMBER="${2:-0}"
LIBRARIES=("datashader" "holoviews")

# Change directory to /tmp
pushd /tmp


EXITCODE=0
trap "EXITCODE=1" ERR
set +e

# Clone the specified Python libraries
if [ "$PROJECT" = "all" ]; then
    # Loop through each library and install dependencies
    for LIBRARY in "${LIBRARIES[@]}"
    do
        rapids-logger "Clone $LIBRARY"
        # Clone the repository
        git clone https://github.com/holoviz/$LIBRARY.git

        rapids-logger "Install $LIBRARY"

        # Change directory to the library
        pushd $LIBRARY
        # Run setup.py with test dependencies
        python -m pip install .[tests]

        rapids-logger "Run GPU tests for $LIBRARY"

        python -m pytest $LIBRARY/tests/ --numprocesses=8 --dist=worksteal --gpu

        popd
    done
else
    rapids-logger "Clone $PROJECT"
    git clone https://github.com/pyviz/$PROJECT.git

    # Check if PR_NUMBER is a non-empty, valid number
    if [ "$PR_NUMBER" -ne 0 ] && [ "$PR_NUMBER" -eq "$PR_NUMBER" ] 2>/dev/null; then
        rapids-logger "checkout PR $PR_NUMBER"
        # Fetch the pull request and check it out
        git fetch origin pull/$PR_NUMBER/head:pr/$PR_NUMBER
        git checkout pr/$PR_NUMBER
    fi
    rapids-logger "Install $PROJECT"

    # Change directory to the specified project
    pushd $PROJECT
    # Run setup.py with test dependencies
    python -m pip install .[tests]


    rapids-logger "Run GPU tests for $PROJECT"

    python -m pytest $PROJECT/tests/ --numprocesses=8 --dist=worksteal --gpu

    popd
fi

rapids-logger "Test script exiting with value: $EXITCODE"
exit ${EXITCODE}
