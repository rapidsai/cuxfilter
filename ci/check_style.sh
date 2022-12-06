#!/bin/bash
# Copyright (c) 2020-2022, NVIDIA CORPORATION.

set -euo pipefail

rapids-logger "Create checks conda environment"
. /opt/conda/etc/profile.d/conda.sh

rapids-dependency-file-generator \
  --output conda \
  --file_key checks \
  --matrix "cuda=${RAPIDS_CUDA_VERSION%.*};arch=$(arch);py=${RAPIDS_PY_VERSION}" | tee env.yaml

rapids-mamba-retry env create --force -f env.yaml -n checks
conda activate checks

set +e

# Run black and get results/return code
BLACK=$(black --check python)
BLACK_RETVAL=$?

# Run flake8 and get results/return code
FLAKE=$(flake8 --config=python/.flake8 python)
FLAKE_RETVAL=$?

if [ "$BLACK_RETVAL" != "0" ]; then
  echo -e "\n\n>>>> FAILED: black style check; begin output\n\n"
  echo -e "$BLACK"
  echo -e "\n\n>>>> FAILED: black style check; end output\n\n"
else
  echo -e "\n\n>>>> PASSED: black style check\n\n"
fi

if [ "$FLAKE_RETVAL" != "0" ]; then
  echo -e "\n\n>>>> FAILED: flake8 style check; begin output\n\n"
  echo -e "$FLAKE"
  echo -e "\n\n>>>> FAILED: flake8 style check; end output\n\n"
else
  echo -e "\n\n>>>> PASSED: flake8 style check\n\n"
fi

RETVALS=($BLACK_RETVAL $FLAKE_RETVAL)
IFS=$'\n'
RETVAL=$(echo "${RETVALS[*]}" | sort -nr | head -n1)

exit $RETVAL
