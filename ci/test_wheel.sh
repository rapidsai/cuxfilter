#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2023-2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

set -eou pipefail

source rapids-init-pip

CUXFILTER_WHEELHOUSE=$(rapids-download-from-github "$(rapids-package-name wheel_python cuxfilter --pure --cuda "${RAPIDS_CUDA_VERSION}")")

# echo to expand wildcard before adding `[extra]` requires for pip
rapids-pip-retry install "$(echo "${CUXFILTER_WHEELHOUSE}"/cuxfilter*.whl)[test]"

python -m pytest -n 8 ./python/cuxfilter/tests
