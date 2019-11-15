set -e

echo "Building cuXfilter"
conda build conda/recipes/cuXfilter --python=$PYTHON
