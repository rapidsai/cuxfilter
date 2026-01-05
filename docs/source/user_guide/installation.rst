Installation
============

Conda
-----
For the most customized way of installing RAPIDS and cuxfilter, visit the selector on the `RAPIDS Installation Guide <https://docs.rapids.ai/install>`_.

.. code-block:: bash

    # CUDA 13
    conda install -c rapidsai -c conda-forge cuxfilter=26.02 cuda-version=13.1

    # CUDA 12
    conda install -c rapidsai -c conda-forge cuxfilter=26.02 cuda-version=12.9

PyPI
----
Install cuxfilter from PyPI using pip:

.. code-block:: bash

    # CUDA 13
    pip install cuxfilter-cu13 -extra-index-url=https://pypi.nvidia.com

    # CUDA 12
    pip install cuxfilter-cu12 -extra-index-url=https://pypi.nvidia.com


Docker container
----------------
For the most customized way of installing RAPIDS and cuxfilter, visit the selector on the `RAPIDS Installation Guide <https://docs.rapids.ai/install>`_.

cuxfilter Docker example installation:

.. code-block:: bash

    docker run --gpus all --pull always --rm -it \
        --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 \
        rapidsai/base:25.12-cuda13-py3.13

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
