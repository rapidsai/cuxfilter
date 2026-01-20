#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2023-2026, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

package_dir="python"

source rapids-date-string
source rapids-init-pip

rapids-generate-version > ./VERSION

cd "${package_dir}"

RAPIDS_PIP_WHEEL_ARGS=(
  -w "${RAPIDS_WHEEL_BLD_OUTPUT_DIR}"
  -v
  --no-deps
  --disable-pip-version-check
)

# unset PIP_CONSTRAINT (set by rapids-init-pip)... it doesn't affect builds as of pip 25.3, and
# results in an error from 'pip wheel' when set and --build-constraint is also passed
unset PIP_CONSTRAINT
rapids-pip-retry wheel \
    "${RAPIDS_PIP_WHEEL_ARGS[@]}" \
    .

# Pure wheels can be installed on any OS and we want to avoid users being able
# to begin installing them on Windows or OSX when we know that the dependencies
# won't work / be available.
for wheel in "${RAPIDS_WHEEL_BLD_OUTPUT_DIR}"/*-py3-none-any.whl; do
    rapids-logger "Retagging pure Python wheel: ${wheel}"

    # Pull the version of GLIBC used in the wheel build container
    glibc_version=$(python -c 'import os; print(os.confstr("CS_GNU_LIBC_VERSION").split()[-1].replace(".", "_"))')
    # Retag for manylinux x86_64 and manylinux aarch64
    # substituting in the glibc_version gathered above
    wheel tags \
        --platform-tag="manylinux_${glibc_version}_x86_64.manylinux_${glibc_version}_aarch64" \
        --remove "${wheel}"

    rapids-logger "Successfully retagged wheel for manylinux platforms"
done

../ci/validate_wheel.sh "${RAPIDS_WHEEL_BLD_OUTPUT_DIR}"

RAPIDS_PACKAGE_NAME="$(rapids-package-name wheel_python cuxfilter --pure --cuda "${RAPIDS_CUDA_VERSION}")"
export RAPIDS_PACKAGE_NAME
