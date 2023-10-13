#!/bin/bash
# Copyright (c) 2022, NVIDIA CORPORATION.

set -euo pipefail

source rapids-env-update

rapids-print-env

package_name="cuxfilter"
package_dir="python"

version=$(rapids-generate-version)
commit=$(git rev-parse HEAD)

version_file="${package_dir}/${package_name}/_version.py"
sed -i "/^__version__/ s/= .*/= ${version}/g" ${version_file}
sed -i "/^__git_commit__/ s/= .*/= \"${commit}\"/g" ${version_file}

rapids-logger "Begin py build"

# TODO: Remove `--no-test` flag once importing on a CPU
# node works correctly
RAPIDS_PACKAGE_VERSION=${version} rapids-conda-retry mambabuild \
  --no-test \
  conda/recipes/cuxfilter

rapids-upload-conda-to-s3 python
