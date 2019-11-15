set -e

echo "Building cuxfilter"
conda build conda/recipes/cuxfilter --python=$PYTHON
