#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2023-2026, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

set -eou pipefail

source rapids-init-pip

CUXFILTER_WHEELHOUSE=$(rapids-download-from-github "$(rapids-package-name wheel_python cuxfilter --pure --cuda "${RAPIDS_CUDA_VERSION}")")

# generate constraints (possibly pinning to oldest support versions of dependencies)
rapids-generate-pip-constraints test_python "${PIP_CONSTRAINT}"

# notes:
#
#   * echo to expand wildcard before adding `[test]` requires for pip
#   * just providing --constraint="${PIP_CONSTRAINT}" to be explicit, and because
#     that environment variable is ignored if any other --constraint are passed via the CLI
#
rapids-pip-retry install \
    --prefer-binary \
    --constraint "${PIP_CONSTRAINT}" \
    "$(echo "${CUXFILTER_WHEELHOUSE}"/cuxfilter*.whl)[test]"

python -m pytest -n 8 ./python/cuxfilter/tests
