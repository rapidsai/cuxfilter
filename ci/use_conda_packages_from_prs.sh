#!/bin/bash

LIBCUSPATIAL_CHANNEL=$(rapids-get-pr-conda-artifact cuspatial 1441 cpp)
CUSPATIAL_CHANNEL=$(rapids-get-pr-conda-artifact cuspatial 1441 python)

conda config --system --add channels "${LIBCUSPATIAL_CHANNEL}"
conda config --system --add channels "${CUSPATIAL_CHANNEL}"
