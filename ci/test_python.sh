#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2022-2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

. /opt/conda/etc/profile.d/conda.sh

rapids-logger "Configuring conda strict channel priority"
conda config --set channel_priority strict

rapids-logger "Downloading artifacts from previous jobs"
PYTHON_CHANNEL=$(rapids-download-from-github "$(rapids-package-name conda_python cuxfilter --pure --cuda "${RAPIDS_CUDA_VERSION}")")

rapids-logger "Generate Python testing dependencies"
rapids-dependency-file-generator \
  --output conda \
  --file-key test_python \
  --matrix "cuda=${RAPIDS_CUDA_VERSION%.*};arch=$(arch);py=${RAPIDS_PY_VERSION}" \
  --prepend-channel "${PYTHON_CHANNEL}" \
  | tee env.yaml

rapids-mamba-retry env create --yes -f env.yaml -n test

# Temporarily allow unbound variables for conda activation.
set +u
conda activate test
set -u

RAPIDS_TESTS_DIR=${RAPIDS_TESTS_DIR:-"${PWD}/test-results"}
RAPIDS_COVERAGE_DIR=${RAPIDS_COVERAGE_DIR:-"${PWD}/coverage-results"}
mkdir -p "${RAPIDS_TESTS_DIR}" "${RAPIDS_COVERAGE_DIR}"

rapids-print-env

rapids-logger "Check GPU usage"
nvidia-smi

EXITCODE=0
trap "EXITCODE=1" ERR
set +e

rapids-logger "pytest cuxfilter"
pushd python/
pytest \
  --cache-clear \
  --junitxml="${RAPIDS_TESTS_DIR}/junit-cuxfilter.xml" \
  --numprocesses=8 \
  --dist=worksteal \
  --cov-config=.coveragerc \
  --cov=cuxfilter \
  --cov-report=xml:"${RAPIDS_COVERAGE_DIR}/cuxfilter-coverage.xml" \
  --cov-report=term
popd

rapids-logger "Test script exiting with value: $EXITCODE"
exit ${EXITCODE}
