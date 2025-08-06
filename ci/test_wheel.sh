#!/bin/bash
# Copyright (c) 2023-2025, NVIDIA CORPORATION.

set -eou pipefail

source rapids-init-pip

RAPIDS_PY_CUDA_SUFFIX="$(rapids-wheel-ctk-name-gen "${RAPIDS_CUDA_VERSION}")"
CUXFILTER_WHEELHOUSE=$(RAPIDS_PY_WHEEL_NAME="cuxfilter_${RAPIDS_PY_CUDA_SUFFIX}" RAPIDS_PY_WHEEL_PURE="1" rapids-download-wheels-from-github python)

# echo to expand wildcard before adding `[extra]` requires for pip
rapids-pip-retry install "$(echo "${CUXFILTER_WHEELHOUSE}"/cuxfilter*.whl)[test]"

python -m pytest -n 8 ./python/cuxfilter/tests
