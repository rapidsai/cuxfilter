#!/bin/bash
# Copyright (c) 2020, NVIDIA CORPORATION.
#################################
# cuXfilter Docs build script for CI #
#################################

if [ -z "$PROJECT_WORKSPACE" ]; then
    echo ">>>> ERROR: Could not detect PROJECT_WORKSPACE in environment"
    echo ">>>> WARNING: This script contains git commands meant for automated building, do not run locally"
    exit 1
fi

export DOCS_WORKSPACE=$WORKSPACE/docs
export PATH=/conda/bin:/usr/local/cuda/bin:$PATH
export HOME=$WORKSPACE
export PROJECT_WORKSPACE=/rapids/cuxfilter
export LIBCUDF_KERNEL_CACHE_PATH="$HOME/.jitify-cache"
export NIGHTLY_VERSION=$(echo $BRANCH_VERSION | awk -F. '{print $2}')
export PROJECTS=(cuxfilter)

logger "Check environment..."
env

logger "Check GPU usage..."
nvidia-smi

logger "Activate conda env..."
source activate rapids


logger "Check versions..."
python --version
$CC --version
$CXX --version
conda list

# Build Python docs
logger "Build Sphinx docs..."
cd $PROJECT_WORKSPACE/docs
make html

#Commit to Website
cd $DOCS_WORKSPACE

for PROJECT in ${PROJECTS[@]}; do
    if [ ! -d "api/$PROJECT/$BRANCH_VERSION" ]; then
        mkdir -p api/$PROJECT/$BRANCH_VERSION
    fi
    rm -rf $DOCS_WORKSPACE/api/$PROJECT/$BRANCH_VERSION/*	
done

mv $PROJECT_WORKSPACE/docs/build/html/* $DOCS_WORKSPACE/api/cuxfilter/$BRANCH_VERSION

