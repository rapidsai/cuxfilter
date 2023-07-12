#!/bin/bash
# Copyright (c) 2023, NVIDIA CORPORATION.
#
# Usage: bash apply_wheel_modifications.sh <new_version> <cuda_suffix>

VERSION=${1}
CUDA_SUFFIX=${2}

# pyproject.toml versions
sed -i "s/^version = .*/version = \"${VERSION}\"/g" python/pyproject.toml

# cuxfilter pyproject.toml cuda suffixes
sed -i "s/^name = \"cuxfilter\"/name = \"cuxfilter${CUDA_SUFFIX}\"/g" python/pyproject.toml
# Need to provide the == to avoid modifying the URL
sed -i "s/\"cudf==/\"cudf${CUDA_SUFFIX}==/g" python/pyproject.toml
sed -i "s/\"cuspatial==/\"cuspatial${CUDA_SUFFIX}==/g" python/pyproject.toml
sed -i "s/\"dask-cudf==/\"dask-cudf${CUDA_SUFFIX}==/g" python/pyproject.toml

if [[ $CUDA_SUFFIX == "-cu12" ]]; then
    sed -i "s/cupy-cuda11x/cupy-cuda12x/g" python/pyproject.toml
fi
