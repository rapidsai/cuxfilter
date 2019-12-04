# Copyright (c) 2018-2019, NVIDIA CORPORATION.

# This assumes the script is executed from the root of the repo directory
pip install git+https://github.com/rapidsai/cuDataShader.git --upgrade --no-deps
./build.sh cuxfilter
