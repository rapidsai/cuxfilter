Installation
============

Conda
-----
For the most customized way of installing RAPIDS and cuxfilter, visit the selector on the RAPIDS `Install Page <https://docs.rapids.ai/install>`_.

.. code-block:: bash

    # for CUDA 12.0
    conda install -c rapidsai -c conda-forge -c nvidia \
        cuxfilter=24.02 python=3.10 cuda-version=12.0

    # for CUDA 11.8
    conda install -c rapidsai -c conda-forge -c nvidia \
        cuxfilter=24.02 python=3.10 cuda-version=11.8

PyPI
----
Install cuxfilter from PyPI using pip:

.. code-block:: bash

    # for CUDA 12.0
    pip install cuxfilter-cu12 -extra-index-url=https://pypi.nvidia.com

    # for CUDA 11.8
    pip install cuxfilter-cu11 -extra-index-url=https://pypi.nvidia.com


Docker container
----------------
For the most customized way of installing RAPIDS and cuxfilter, visit the selector on the RAPIDS `Install Page <https://docs.rapids.ai/install>`_.

cuxfilter docker example installation for cuda 12.0, ubuntu 20.04:

.. code-block:: bash

    # ex. for CUDA 11.8
    docker pull rapidsai/rapidsai:cuda12.0-runtime-ubuntu20.04
    docker run --gpus all --rm -it -p 8888:8888 -p 8787:8787 -p 8786:8786 \
        rapidsai/rapidsai:cuda11.8-runtime-ubuntu20.04

    # open http://localhost:8888

Build/Install from Source
-------------------------

See `build instructions <https://github.com/rapidsai/cuxfilter/blob/HEAD/CONTRIBUTING.md#script-to-build-cuxfilter-from-source>`_ on our GitHub.



Troubleshooting
---------------

If the guide below doesn't help you resolve your issue, please `file an issue <https://github.com/rapidsai/cuxfilter/issues/new/choose>`_ on our GitHub.

Install jupyterlab dependencies
********************************

If you have issues with charts not rendering in the jupyterlab notebook, please make sure you have the following installed in your environment:

.. code-block:: bash

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz
    jupyter labextension install @bokeh/jupyter_bokeh


Download datasets
-----------------

1. Automatically download datasets
***********************************

The notebooks inside `python/notebooks` already have a check function which verifies whether the example dataset is downloaded, and downloads if not present.

2. Download manually
********************

While in the directory you want the datasets to be saved, execute the following

.. code-block:: bash

    #go the the environment where cuxfilter is installed. Skip if in a docker container
    conda activate test_env

    #download and extract the datasets
    curl https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2015-01.csv --create-dirs -o ./nyc_taxi.csv
    curl https://data.rapids.ai/viz-data/146M_predictions_v2.arrow.gz --create-dirs -o ./146M_predictions_v2.arrow.gz
    curl https://data.rapids.ai/viz-data/auto_accidents.arrow.gz --create-dirs -o ./auto_accidents.arrow.gz

    python -c "from cuxfilter.sampledata import datasets_check; datasets_check(base_dir='./')"
