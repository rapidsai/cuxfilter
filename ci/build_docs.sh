#!/bin/bash

set -euo pipefail

rapids-logger "Create test conda environment"
. /opt/conda/etc/profile.d/conda.sh

rapids-dependency-file-generator \
    --output conda \
    --file-key docs \
    --matrix "cuda=${RAPIDS_CUDA_VERSION%.*};arch=$(arch);py=${RAPIDS_PY_VERSION}" | tee env.yaml

rapids-mamba-retry env create --yes -f env.yaml -n docs
conda activate docs

rapids-print-env

rapids-logger "Downloading artifacts from previous jobs"

PYTHON_CHANNEL=$(rapids-download-conda-from-s3 python)

rapids-mamba-retry install \
    --channel "${PYTHON_CHANNEL}" \
    cuxfilter

export RAPIDS_VERSION="$(rapids-version)"
export RAPIDS_VERSION_MAJOR_MINOR="$(rapids-version-major-minor)"
export RAPIDS_VERSION_NUMBER="$RAPIDS_VERSION_MAJOR_MINOR"
export RAPIDS_DOCS_DIR="$(mktemp -d)"

rapids-logger "Build Python docs"
pushd docs
sphinx-build -b dirhtml ./source _html
mkdir -p "${RAPIDS_DOCS_DIR}/cuxfilter/"html
mv _html/* "${RAPIDS_DOCS_DIR}/cuxfilter/html"
popd

rapids-upload-docs
