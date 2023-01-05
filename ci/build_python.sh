#!/bin/bash
# Copyright (c) 2022, NVIDIA CORPORATION.

set -euo pipefail

source rapids-env-update

rapids-print-env

rapids-logger "Begin py build"

# TODO: Remove `--no-test` flag once importing on a CPU
# node works correctly
rapids-mamba-retry mambabuild \
  --no-test \
  conda/recipes/cuxfilter

rapids-upload-conda-to-s3 python
