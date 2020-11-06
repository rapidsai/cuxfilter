set -e

echo "Building cuxfilter"
gpuci_conda_retry build conda/recipes/cuxfilter --python=$PYTHON
