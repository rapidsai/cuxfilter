#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2020-2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

. /opt/conda/etc/profile.d/conda.sh

rapids-logger "Downloading artifacts from previous jobs"
PYTHON_CHANNEL=$(rapids-download-from-github "$(rapids-package-name "conda_python" cuxfilter --pure)")

rapids-logger "Generate notebook testing dependencies"
rapids-dependency-file-generator \
  --output conda \
  --file-key test_notebooks \
  --matrix "cuda=${RAPIDS_CUDA_VERSION%.*};arch=$(arch);py=${RAPIDS_PY_VERSION}" \
  --prepend-channel "${PYTHON_CHANNEL}" \
  | tee env.yaml

rapids-mamba-retry env create --yes -f env.yaml -n test

# Temporarily allow unbound variables for conda activation.
set +u
conda activate test
set -u

rapids-print-env

NBTEST="$(realpath "$(dirname "$0")/utils/nbtest.sh")"
pushd notebooks

# Add notebooks that should be skipped here
# (space-separated list of filenames without paths)
SKIPNBS=""

EXITCODE=0
trap "EXITCODE=1" ERR
set +e
# shellcheck disable=SC2044
readarray -d '' nb_files < <(find . -name "*.ipynb")
for nb in "${nb_files[@]}"; do
    nbBasename=$(basename "${nb}")
    # Skip all notebooks that use dask (in the code or even in their name)
    if (echo "${nb}" | grep -qi dask) || (grep -q dask "${nb}"); then
        echo "--------------------------------------------------------------------------------"
        echo "SKIPPING: ${nb} (suspected Dask usage, not currently automatable)"
        echo "--------------------------------------------------------------------------------"
    elif (echo " ${SKIPNBS} " | grep -q " ${nbBasename} "); then
        echo "--------------------------------------------------------------------------------"
        echo "SKIPPING: ${nb} (listed in skip list)"
        echo "--------------------------------------------------------------------------------"
    else
        nvidia-smi
        ${NBTEST} "${nbBasename}"
    fi
done

rapids-logger "Test script exiting with value: $EXITCODE"
exit ${EXITCODE}
