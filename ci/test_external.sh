#!/bin/bash
# Copyright (c) 2023, NVIDIA CORPORATION.

set -e

rapids-logger "Create test_external conda environment"
. /opt/conda/etc/profile.d/conda.sh

# Install external dependencies into test_external conda environment
rapids-mamba-retry env update -f ./ci/utils/external_dependencies.yaml

conda activate test_external

# Define input parameter
PROJECT=$1
PR_NUMBER=$2
LIBRARIES=("datashader" "holoviews")

# Change directory to /tmp
pushd /tmp

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
        python -m pip install -e .[tests]

        popd
    done
else
    rapids-logger "Clone $PROJECT"
    git clone https://github.com/pyviz/$PROJECT.git

    # Check if PR_NUMBER is a non-empty, valid number
    if [ -n "$PR_NUMBER" ] && [ "$PR_NUMBER" -eq "$PR_NUMBER" ] 2>/dev/null; then
        rapids-logger "checkout PR $PR_NUMBER"
        # Fetch the pull request and check it out
        git fetch origin pull/$PR_NUMBER/head:pr/$PR_NUMBER
        git checkout pr/$PR_NUMBER
    fi
    rapids-logger "Install $PROJECT"

    # Change directory to the specified project
    pushd $PROJECT
    # Run setup.py with test dependencies
    python -m pip install -e .[tests]
    popd
fi

FILES=""
# Install and run tests
if [ "$PROJECT" = "all" ]; then
    # Loop through each library and install dependencies
    for LIBRARY in "${LIBRARIES[@]}"
    do
        rapids-logger "gathering GPU tests for $LIBRARY"
        TEST_DIR="$LIBRARY/$LIBRARY/tests"
        # Find all Python scripts containing the keywords cudf or dask_cudf except test_quadmesh.py
        FILES+=" $(grep -l -R -e 'cudf' --include='*.py' "$TEST_DIR" | grep -v test_quadmesh.py)"
    done
else
    rapids-logger "gathering GPU tests for $PROJECT"
    TEST_DIR="$PROJECT/$PROJECT/tests"
    # Find all Python scripts containing the keywords cudf or dask_cudf
    FILES+=$(grep -l -R -e 'cudf' --include='*.py' "$TEST_DIR")
fi

EXITCODE=0
trap "EXITCODE=1" ERR
set +e

rapids-logger "running all gathered tests"
DATASHADER_TEST_GPU=1 pytest --numprocesses=8 $FILES

if [[ "$PROJECT" = "all" ]] || [[ "$PROJECT" = "datashader" ]]; then
    # run test_quadmesh.py separately as dask.array tests fail with numprocesses
    rapids-logger "running test_quadmesh.py"
    DATASHADER_TEST_GPU=1 pytest datashader/datashader/tests/test_quadmesh.py
fi

rapids-logger "Test script exiting with value: $EXITCODE"
exit ${EXITCODE}
