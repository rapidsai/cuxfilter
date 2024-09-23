#!/bin/bash

RAPIDS_PY_CUDA_SUFFIX="$(rapids-wheel-ctk-name-gen ${RAPIDS_CUDA_VERSION})"

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
cuspatial-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${CUSPATIAL_CHANNEL}/cuspatial_*.whl)
libcuspatial-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${LIBCUSPATIAL_CHANNEL}/libcuspatial_*.whl)
cuproj-${RAPIDS_PY_CUDA_SUFFIX} @ file://$(echo ${CUPROJ_CHANNEL}/cuproj_*.whl)
EOF

export PIP_CONSTRAINT=/tmp/constraints.txt
