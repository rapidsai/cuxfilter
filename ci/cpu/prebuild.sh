#!/usr/bin/env bash

#Upload cuxfilter once per PYTHON
if [[ "$CUDA" == "9.2" ]]; then
    export UPLOAD_CUDF=1
else
    export UPLOAD_CUDF=0
fi