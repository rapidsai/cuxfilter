#!/bin/bash

RAPIDS_PY_CUDA_SUFFIX="$(rapids-wheel-ctk-name-gen ${RAPIDS_CUDA_VERSION})"

LIBRMM_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=rmm_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact rmm 1678 cpp
)
RMM_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=rmm_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact rmm 1678 python
)

CUDF_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=cudf_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact cudf 16806 python
)
LIBCUDF_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=libcudf_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact cudf 16806 cpp
)
PYLIBCUDF_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=pylibcudf_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact cudf 16806 python
)
DASK_CUDF_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=dask_cudf_${RAPIDS_PY_CUDA_SUFFIX} \
  RAPIDS_PY_WHEEL_PURE=1 \
    rapids-get-pr-wheel-artifact cudf 16806 python
)

CUSPATIAL_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=cuspatial_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact cuspatial 1441 python
)
CUPROJ_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=cuproj_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact cuspatial 1441 python
)
LIBCUSPATIAL_CHANNEL=$(
  RAPIDS_PY_WHEEL_NAME=libcuspatial_${RAPIDS_PY_CUDA_SUFFIX} rapids-get-pr-wheel-artifact cuspatial 1441 cpp
)

cat > /tmp/constraints.txt <<EOF
librmm-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${LIBRMM_CHANNEL}/librmm_*.whl)
rmm-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${RMM_CHANNEL}/rmm_*.whl)
cudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${CUDF_CHANNEL}/cudf_*.whl)
libcudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${LIBCUDF_CHANNEL}/libcudf_*.whl)
pylibcudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${PYLIBCUDF_CHANNEL}/pylibcudf_*.whl)
dask-cudf-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${DASK_CUDF_CHANNEL}/dask_cudf_*.whl)
cuspatial-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${CUSPATIAL_CHANNEL}/cuspatial_*.whl)
libcuspatial-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${LIBCUSPATIAL_CHANNEL}/libcuspatial_*.whl)
cuproj-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${CUPROJ_CHANNEL}/cuproj_*.whl)
EOF

export PIP_CONSTRAINT=/tmp/constraints.txt
