#!/bin/bash
# Copyright (c) 2023, NVIDIA CORPORATION.

set -eou pipefail

RAPIDS_PY_CUDA_SUFFIX="$(rapids-wheel-ctk-name-gen ${RAPIDS_CUDA_VERSION})"
RAPIDS_PY_WHEEL_NAME="cuxfilter_${RAPIDS_PY_CUDA_SUFFIX}" RAPIDS_PY_WHEEL_PURE="1" rapids-download-wheels-from-s3 ./dist

source ./ci/use_wheels_from_prs.sh

# echo to expand wildcard before adding `[extra]` requires for pip
python -m pip install $(echo ./dist/cuxfilter*.whl)[test]

python -m pytest -n 8 ./python/cuxfilter/tests
