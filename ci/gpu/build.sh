#!/bin/bash
# COPYRIGHT (c) 2020-2002, NVIDIA CORPORATION.
##############################################
# cuXfilter GPU build and test script for CI #
##############################################
set -e
NUMARGS=$#
ARGS=$*

# Arg parsing function
function hasArg {
    (( ${NUMARGS} != 0 )) && (echo " ${ARGS} " | grep -q " $1 ")
}

# Set path and build parallel level
export PATH=/opt/conda/bin:/usr/local/cuda/bin:$PATH
export PARALLEL_LEVEL=${PARALLEL_LEVEL:-4}
export CUDA_REL=${CUDA_VERSION%.*}

# Set home to the job's workspace
export HOME="$WORKSPACE"

# Parse git describe
cd "$WORKSPACE"
export GIT_DESCRIBE_TAG=`git describe --tags`
export MINOR_VERSION=`echo $GIT_DESCRIBE_TAG | grep -o -E '([0-9]+\.[0-9]+)'`
unset GIT_DESCRIBE_TAG

# Set `LIBCUDF_KERNEL_CACHE_PATH` environment variable to $HOME/.jitify-cache because
# it's local to the container's virtual file system, and not shared with other CI jobs
# like `/tmp` is.
export LIBCUDF_KERNEL_CACHE_PATH="$HOME/.jitify-cache"

function remove_libcudf_kernel_cache_dir {
    EXITCODE=$?
    gpuci_logger "removing kernel cache dir: $LIBCUDF_KERNEL_CACHE_PATH"
    rm -rf "$LIBCUDF_KERNEL_CACHE_PATH" || gpuci_logger "could not rm -rf $LIBCUDF_KERNEL_CACHE_PATH"
    exit $EXITCODE
}

trap remove_libcudf_kernel_cache_dir EXIT

mkdir -p "$LIBCUDF_KERNEL_CACHE_PATH" || gpuci_logger "could not mkdir -p $LIBCUDF_KERNEL_CACHE_PATH"

################################################################################
# SETUP - Check environment
################################################################################

gpuci_logger "Check environment"
env

gpuci_logger "Check GPU usage"
nvidia-smi

gpuci_logger "Activate conda env"
. /opt/conda/etc/profile.d/conda.sh
conda activate rapids

gpuci_logger "Check versions"
python --version
$CC --version
$CXX --version

conda info
conda config --show-sources
conda list --show-channel-urls

################################################################################
# BUILD - Build cuxfilter
################################################################################

# TODO: Move boa install to gpuci/rapidsai
gpuci_mamba_retry install boa

gpuci_logger "Build and install cuxfilter"
cd "${WORKSPACE}"
CONDA_BLD_DIR="${WORKSPACE}/.conda-bld"
gpuci_conda_retry mambabuild  --croot "${CONDA_BLD_DIR}" conda/recipes/cuxfilter --python=$PYTHON
gpuci_mamba_retry install -c "${CONDA_BLD_DIR}" cuxfilter

################################################################################
# TEST - Run pytest
################################################################################

set +e -Eo pipefail
EXITCODE=0
trap "EXITCODE=1" ERR

if hasArg --skip-tests; then
    gpuci_logger "Skipping Tests"
else
    gpuci_logger "Install tests dependencies"
    gpuci_mamba_retry install "cugraph=${MINOR_VERSION}.*"

    gpuci_logger "Check GPU usage"
    nvidia-smi

    cd "$WORKSPACE/python/cuxfilter/tests"
    gpuci_logger "Python py.test for cuxfilter"
    py.test --cache-clear --junitxml="$WORKSPACE/junit-cuxfilter.xml" -v

    "$WORKSPACE/ci/gpu/test-notebooks.sh" 2>&1 | tee nbtest.log
    python "$WORKSPACE/ci/utils/nbtestlog2junitxml.py" nbtest.log
fi

return ${EXITCODE}
