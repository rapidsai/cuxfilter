#!/usr/bin/env bash

#Upload cuxfilter once per PYTHON
if [[ "$CUDA" == "9.2" ]]; then
    export UPLOAD_CUXFILTER=1
else
    export UPLOAD_CUXFILTER=0
fi
