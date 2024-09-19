#!/bin/bash
# Copyright (c) 2022, NVIDIA CORPORATION.

set -euo pipefail

rapids-configure-conda-channels

source rapids-configure-sccache

source rapids-date-string

source ./ci/use_conda_packages_from_prs.sh

rapids-print-env

rapids-generate-version > ./VERSION

rapids-logger "Begin py build"

conda config --set path_conflict prevent
# TODO: Remove `--no-test` flag once importing on a CPU
# node works correctly
RAPIDS_PACKAGE_VERSION=$(head -1 ./VERSION) rapids-conda-retry mambabuild \
  --no-test \
  conda/recipes/cuxfilter

rapids-upload-conda-to-s3 python
