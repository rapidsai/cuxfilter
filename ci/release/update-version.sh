#!/bin/bash
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

echo "Preparing release $CURRENT_TAG => $NEXT_FULL_TAG"

# Inplace sed replace; workaround for Linux and Mac
function sed_runner() {
    sed -i.bak ''"$1"'' $2 && rm -f ${2}.bak
}

# RTD update
sed_runner 's/version = .*/version = '"'${NEXT_SHORT_TAG}'"'/g' docs/source/conf.py
sed_runner 's/release = .*/release = '"'${NEXT_FULL_TAG}'"'/g' docs/source/conf.py

# bump cudf
for FILE in conda/environments/*.yaml dependencies.yaml; do
  sed_runner "s/cudf=.*/cudf=${NEXT_SHORT_TAG}/g" ${FILE};
  sed_runner "s/cuspatial=.*/cuspatial=${NEXT_SHORT_TAG}/g" ${FILE};
  sed_runner "s/dask-cuda=.*/dask-cuda=${NEXT_SHORT_TAG}/g" ${FILE};
  sed_runner "s/dask-cudf=.*/dask-cudf=${NEXT_SHORT_TAG}/g" ${FILE};
done

# README.md update
sed_runner "s/version == ${CURRENT_SHORT_TAG}/version == ${NEXT_SHORT_TAG}/g" README.md
sed_runner "s/cuxfilter=${CURRENT_SHORT_TAG}/cuxfilter=${NEXT_SHORT_TAG}/g" README.md
