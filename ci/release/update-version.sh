#!/bin/bash
# Copyright (c) 2020-2023, NVIDIA CORPORATION.
#############################
# cuxfilter Version Updater #
#############################

## Usage
# bash update-version.sh <new_version>


# Format is YY.MM.PP - no leading 'v' or trailing 'a'
NEXT_FULL_TAG=$1

# Get current version
CURRENT_TAG=$(git tag --merged HEAD | grep -xE '^v.*' | sort --version-sort | tail -n 1 | tr -d 'v')
CURRENT_MAJOR=$(echo $CURRENT_TAG | awk '{split($0, a, "."); print a[1]}')
CURRENT_MINOR=$(echo $CURRENT_TAG | awk '{split($0, a, "."); print a[2]}')
CURRENT_PATCH=$(echo $CURRENT_TAG | awk '{split($0, a, "."); print a[3]}')
CURRENT_SHORT_TAG=${CURRENT_MAJOR}.${CURRENT_MINOR}

#Get <major>.<minor> for next version
NEXT_MAJOR=$(echo $NEXT_FULL_TAG | awk '{split($0, a, "."); print a[1]}')
NEXT_MINOR=$(echo $NEXT_FULL_TAG | awk '{split($0, a, "."); print a[2]}')
NEXT_SHORT_TAG=${NEXT_MAJOR}.${NEXT_MINOR}

# Need to distutils-normalize the original version
NEXT_SHORT_TAG_PEP440=$(python -c "from setuptools.extern import packaging; print(packaging.version.Version('${NEXT_SHORT_TAG}'))")

echo "Preparing release $CURRENT_TAG => $NEXT_FULL_TAG"

# Inplace sed replace; workaround for Linux and Mac
function sed_runner() {
    sed -i.bak ''"$1"'' $2 && rm -f ${2}.bak
}

# RTD update
sed_runner 's/version = .*/version = '"'${NEXT_SHORT_TAG}'"'/g' docs/source/conf.py
sed_runner 's/release = .*/release = '"'${NEXT_FULL_TAG}'"'/g' docs/source/conf.py
# docs update
sed_runner "/cuxfilter=[0-9]\{2\}.[0-9]\{2\}/ s/=[0-9]\{2\}.[0-9]\{2\}/=${NEXT_SHORT_TAG}/g" docs/source/user_guide/installation.rst

# Centralized version file update
echo "${NEXT_FULL_TAG}" > VERSION


DEPENDENCIES=(
  cudf
  cuxfilter
  dask-cuda
  dask-cudf
  cugraph
  cuspatial
)
for DEP in "${DEPENDENCIES[@]}"; do
  for FILE in dependencies.yaml conda/environments/*.yaml ci/utils/external_dependencies.yaml; do
    sed_runner "/-.* ${DEP}\(-cu[[:digit:]]\{2\}\)\{0,1\}==/ s/==.*/==${NEXT_SHORT_TAG_PEP440}.*/g" "${FILE}"
  done
  for FILE in python/pyproject.toml; do
    sed_runner "/\"${DEP}\(-cu[[:digit:]]\{2\}\)\{0,1\}==/ s/==.*\"/==${NEXT_SHORT_TAG_PEP440}.*\"/g" "${FILE}"
  done
done

# README.md update
sed_runner "/version == / s/== .*\`/== ${NEXT_SHORT_TAG}\`/g" README.md
sed_runner "/cuxfilter=[0-9]\{2\}.[0-9]\{2\}/ s/=[0-9]\{2\}.[0-9]\{2\}/=${NEXT_SHORT_TAG}/g" README.md


# CI files
for FILE in .github/workflows/*.yaml; do
  sed_runner "/shared-workflows/ s/@.*/@branch-${NEXT_SHORT_TAG}/g" ${FILE};
done

sed_runner "s/RAPIDS_VERSION_NUMBER=\".*/RAPIDS_VERSION_NUMBER=\"${NEXT_SHORT_TAG}\"/g" ci/build_docs.sh
sed_runner "s/RAPIDS_VERSION=.*/RAPIDS_VERSION=${NEXT_SHORT_TAG}.*/g" ci/test_external.sh
