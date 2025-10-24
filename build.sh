#!/bin/bash

# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

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
REPODIR=$(cd "$(dirname "$0")"; pwd)
VALIDARGS="clean cuxfilter -n -h"
HELP="$0 [clean] [cuxfilter] [-v] [-g] [-n] [-h]
   clean        - remove all existing build artifacts and configuration (start
                  over)
   cuxfilter    - build the cuxfilter library only
   -h           - print this text
"
CUXFILTER_BUILD_DIR=${REPODIR}/python/cuxfilter/build
BUILD_DIRS="${CUXFILTER_BUILD_DIR}"

# Set defaults for vars that may not have been defined externally
#  FIXME: if INSTALL_PREFIX is not set, check PREFIX, then check
#         CONDA_PREFIX, but there is no fallback from there!
INSTALL_PREFIX=${INSTALL_PREFIX:=${PREFIX:=${CONDA_PREFIX}}}
PARALLEL_LEVEL=${PARALLEL_LEVEL:=""}

function hasArg {
    (( NUMARGS != 0 )) && (echo " ${ARGS} " | grep -q " $1 ")
}

if hasArg -h; then
    echo "${HELP}"
    exit 0
fi

# Check for valid usage
if (( NUMARGS != 0 )); then
    for a in ${ARGS}; do
    if ! (echo " ${VALIDARGS} " | grep -q " ${a} "); then
        echo "Invalid option: ${a}"
        exit 1
    fi
    done
fi

# If clean given, run it prior to any other steps
if hasArg clean; then
    # If the dirs to clean are mounted dirs in a container, the
    # contents should be removed but the mounted dirs will remain.
    # The find removes all contents but leaves the dirs, the rmdir
    # attempts to remove the dirs but can fail safely.
    for bd in ${BUILD_DIRS}; do
    if [ -d "${bd}" ]; then
        find "${bd}" -mindepth 1 -delete
        rmdir "${bd}" || true
    fi
    done
fi

################################################################################

# Build and install the cuxfilter Python package
if (( NUMARGS == 0 )) || hasArg cuxfilter; then

    cd "${REPODIR}"/python
    python -m pip install --no-build-isolation --no-deps --config-settings rapidsai.disable-cuda=true .
fi
