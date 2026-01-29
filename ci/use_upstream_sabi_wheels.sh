#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# initialize PIP_CONSTRAINT
source rapids-init-pip

RAPIDS_PY_CUDA_SUFFIX=$(rapids-wheel-ctk-name-gen "${RAPIDS_CUDA_VERSION}")

if [[ "${RAPIDS_PY_VERSION}" != "3.10" ]]; then

# download wheels, store the directories holding them in variables
LIBRMM_WHEELHOUSE=$(
  RAPIDS_PY_WHEEL_NAME="librmm_${RAPIDS_PY_CUDA_SUFFIX}" rapids-get-pr-artifact rmm 2184 cpp wheel
)
RMM_WHEELHOUSE=$(
  rapids-get-pr-artifact rmm 2184 python wheel --stable
)
LIBCUDF_WHEELHOUSE=$(
  RAPIDS_PY_WHEEL_NAME="libcudf_${RAPIDS_PY_CUDA_SUFFIX}" rapids-get-pr-artifact cudf 20974 cpp wheel
)
PYLIBCUDF_WHEELHOUSE=$(
  rapids-get-pr-artifact cudf 20974 python wheel --stable --pkg_name pylibcudf
)
CUDF_WHEELHOUSE=$(
  rapids-get-pr-artifact cudf 20974 python wheel --stable
)
PYLIBCUGRAPH_WHEELHOUSE=$(rapids-get-pr-artifact cugraph 5388 python wheel --stable --pkg_name pylibcugraph)
LIBCUGRAPH_WHEELHOUSE=$(
  RAPIDS_PY_WHEEL_NAME="libcugraph_${RAPIDS_PY_CUDA_SUFFIX}" rapids-get-pr-artifact cugraph 5388 cpp wheel
)

cat > "${PIP_CONSTRAINT}" <<EOF
librmm-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${LIBRMM_WHEELHOUSE}"/librmm_*.whl)
rmm-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${RMM_WHEELHOUSE}"/rmm_*.whl)
libcudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${LIBCUDF_WHEELHOUSE}"/libcudf_*.whl)
pylibcudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${PYLIBCUDF_WHEELHOUSE}"/pylibcudf_*.whl)
cudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${CUDF_WHEELHOUSE}"/cudf_*.whl)
libcugraph-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${LIBCUGRAPH_WHEELHOUSE}"/libcugraph_*.whl)
pylibcugraph-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo "${PYLIBCUGRAPH_WHEELHOUSE}"/pylibcugraph_*.whl)
EOF

fi
