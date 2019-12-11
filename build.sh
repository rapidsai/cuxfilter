#!/bin/bash

# Copyright (c) 2019, NVIDIA CORPORATION.

# cuDF build script

# This script is used to build the component(s) in this repo from
# source, and can be called with various options to customize the
# build as needed (see the help output for details)

# Abort script on first error
set -e

NUMARGS=$#
ARGS=$*

# NOTE: ensure all dir changes are relative to the location of this
# script, and that this script resides in the repo dir!
REPODIR=$(cd $(dirname $0); pwd)
VALIDARGS="clean cuxfilter cudatashader -v -g -n --allgpuarch -h"
HELP="$0 [clean] [cuxfilter] [cudatashader] [-v] [-g] [-n] [-h]
   clean        - remove all existing build artifacts and configuration (start
                  over)
   cuxfilter    - build the cuxfilter library only
   cudatashader - build the cudatashader library only
   -v           - verbose build mode
   -g           - build for debug
   -n           - no install step
   --allgpuarch - build for all supported GPU architectures
   -h           - print this text
"
CUXFILTER_BUILD_DIR=${REPODIR}/python/cuxfilter/build
#CUDATASHADER_BUILD_DIR=${REPODIR}/cuDatashader/build
BUILD_DIRS="${CUXFILTER_BUILD_DIR}" #{CUDATASHADER_BUILD_DIR}

# Set defaults for vars modified by flags to this script
VERBOSE=""
BUILD_TYPE=Release
INSTALL_TARGET=install
BENCHMARKS=OFF
BUILD_ALL_GPU_ARCH=0

# Set defaults for vars that may not have been defined externally
#  FIXME: if INSTALL_PREFIX is not set, check PREFIX, then check
#         CONDA_PREFIX, but there is no fallback from there!
INSTALL_PREFIX=${INSTALL_PREFIX:=${PREFIX:=${CONDA_PREFIX}}}
PARALLEL_LEVEL=${PARALLEL_LEVEL:=""}

function hasArg {
    (( ${NUMARGS} != 0 )) && (echo " ${ARGS} " | grep -q " $1 ")
}

if hasArg -h; then
    echo "${HELP}"
    exit 0
fi

# Check for valid usage
if (( ${NUMARGS} != 0 )); then
    for a in ${ARGS}; do
    if ! (echo " ${VALIDARGS} " | grep -q " ${a} "); then
        echo "Invalid option: ${a}"
        exit 1
    fi
    done
fi

# Process flags
if hasArg -v; then
    VERBOSE=1
fi
if hasArg -g; then
    BUILD_TYPE=Debug
fi
if hasArg -n; then
    INSTALL_TARGET=""
fi
if hasArg --allgpuarch; then
    BUILD_ALL_GPU_ARCH=1
fi
if hasArg benchmarks; then
    BENCHMARKS="ON"
fi

# If clean given, run it prior to any other steps
if hasArg clean; then
    # If the dirs to clean are mounted dirs in a container, the
    # contents should be removed but the mounted dirs will remain.
    # The find removes all contents but leaves the dirs, the rmdir
    # attempts to remove the dirs but can fail safely.
    for bd in ${BUILD_DIRS}; do
    if [ -d ${bd} ]; then
        find ${bd} -mindepth 1 -delete
        rmdir ${bd} || true
    fi
    done
fi

if (( ${BUILD_ALL_GPU_ARCH} == 0 )); then
    GPU_ARCH="-DGPU_ARCHS="
    echo "Building for the architecture of the GPU in the system..."
else
    GPU_ARCH="-DGPU_ARCHS=ALL"
    echo "Building for *ALL* supported GPU architectures..."
fi

################################################################################

# Build and install the cuxfilter Python package
if (( ${NUMARGS} == 0 )) || hasArg cuxfilter; then

    cd ${REPODIR}/python
    echo "8"
    if [[ ${INSTALL_TARGET} != "" ]]; then
        python setup.py build_ext --inplace
        python setup.py install --single-version-externally-managed --record=record.txt
    else
        python setup.py build_ext --inplace --library-dir=${LIBCUXFILTER_BUILD_DIR}
    fi
fi

