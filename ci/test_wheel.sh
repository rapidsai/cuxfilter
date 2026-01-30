#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2023-2026, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

set -eou pipefail

RAPIDS_INIT_PIP_REMOVE_NVIDIA_INDEX="true"
export RAPIDS_INIT_PIP_REMOVE_NVIDIA_INDEX
source rapids-init-pip

CUXFILTER_WHEELHOUSE=$(rapids-download-from-github "$(rapids-package-name wheel_python cuxfilter --pure --cuda "${RAPIDS_CUDA_VERSION}")")

# echo to expand wildcard before adding `[extra]` requires for pip
rapids-pip-retry install "$(echo "${CUXFILTER_WHEELHOUSE}"/cuxfilter*.whl)[test]"

python -m pytest -n 8 ./python/cuxfilter/tests
