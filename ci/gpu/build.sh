#!/bin/bash
# Copyright (c) 2018, NVIDIA CORPORATION.
##############################################
# cuXfilter GPU build and test script for CI #
##############################################
set -e
NUMARGS=$#
ARGS=$*

# Logger function for build status output
function logger() {
  echo -e "\n>>>> $@\n"
}

# Arg parsing function
function hasArg {
    (( ${NUMARGS} != 0 )) && (echo " ${ARGS} " | grep -q " $1 ")
}

# Set path and build parallel level
export PATH=/conda/bin:/usr/local/cuda/bin:$PATH
export PARALLEL_LEVEL=4
export CUDA_REL=${CUDA_VERSION%.*}

# Set home to the job's workspace
export HOME=$WORKSPACE

# Parse git describe
cd $WORKSPACE
export GIT_DESCRIBE_TAG=`git describe --tags`
export MINOR_VERSION=`echo $GIT_DESCRIBE_TAG | grep -o -E '([0-9]+\.[0-9]+)'`
# Set `LIBCUDF_KERNEL_CACHE_PATH` environment variable to $HOME/.jitify-cache because
# it's local to the container's virtual file system, and not shared with other CI jobs
# like `/tmp` is.
export LIBCUDF_KERNEL_CACHE_PATH="$HOME/.jitify-cache"

function remove_libcudf_kernel_cache_dir {
    EXITCODE=$?
    logger "removing kernel cache dir: $LIBCUDF_KERNEL_CACHE_PATH"
    rm -rf "$LIBCUDF_KERNEL_CACHE_PATH" || logger "could not rm -rf $LIBCUDF_KERNEL_CACHE_PATH"
    exit $EXITCODE
}

trap remove_libcudf_kernel_cache_dir EXIT

mkdir -p "$LIBCUDF_KERNEL_CACHE_PATH" || logger "could not mkdir -p $LIBCUDF_KERNEL_CACHE_PATH"

################################################################################
# SETUP - Check environment
################################################################################

logger "Check environment..."
env

logger "Check GPU usage..."
nvidia-smi

logger "Activate conda env..."
source activate gdf
conda install "cudf=$MINOR_VERSION.*" "cudatoolkit=$CUDA_REL" "rapids-notebook-env=$MINOR_VERSION.*" \
              "datashader>=0.10.*" "panel=0.6.*" "bokeh=1.*" "geopandas>=0.6.*" "pytest" "pyppeteer" \
              "jupyter-server-proxy" "pyproj>=2.4.*" "nodejs" "dask-cudf=$MINOR_VERSION.*" "dask-cuda=$MINOR_VERSION.*"

logger "Check versions..."
python --version
$CC --version
$CXX --version
conda list

################################################################################
# BUILD - Build cuxfilter from source
################################################################################

logger "Build cuxfilter..."
$WORKSPACE/build.sh clean cuxfilter

################################################################################
# TEST - Run pytest 
################################################################################

if hasArg --skip-tests; then
    logger "Skipping Tests..."
else
    logger "Check GPU usage..."
    nvidia-smi

    cd $WORKSPACE/python/cuxfilter/tests
    logger "Python py.test for cuxfilter..."
    py.test --cache-clear --junitxml=${WORKSPACE}/junit-cuxfilter.xml -v

    ${WORKSPACE}/ci/gpu/test-notebooks.sh 2>&1 | tee nbtest.log
    python ${WORKSPACE}/ci/utils/nbtestlog2junitxml.py nbtest.log
fi
