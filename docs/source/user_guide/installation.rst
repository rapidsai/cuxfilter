Installation
============

Conda
-----
For the most customized way of installing RAPIDS and cuxfilter, visit the selector on the RAPIDS `Install Page <https://docs.rapids.ai/install>`_.

cuxfilter conda example installation:

.. code-block:: bash

    conda install -c rapidsai -c conda-forge -c nvidia \
        cuxfilter=23.6 python=3.10 cudatoolkit=11.8

Docker container
----------------
For the most customized way of installing RAPIDS and cuxfilter, visit the selector on the RAPIDS `Install Page <https://docs.rapids.ai/install>`_.

cuxfilter docker example installation:

.. code-block:: bash

    # ex. for CUDA 11.8
    docker pull rapidsai/rapidsai:cuda11.8-runtime-ubuntu20.04
    docker run --gpus all --rm -it -p 8888:8888 -p 8787:8787 -p 8786:8786 \
        rapidsai/rapidsai:cuda11.8-runtime-ubuntu20.04

    # open http://localhost:8888

Build/Install from Source
-------------------------

See `build instructions <https://github.com/rapidsai/cuxfilter/blob/main/CONTRIBUTING.md#setting-up-your-build-environment>` on our GitHub.



Troubleshooting
---------------

Install jupyterlab dependencies
**********************************

.. code-block:: bash

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz
    jupyter labextension install @bokeh/jupyter_bokeh


libxcomposite.so.1 not found error
*************************************

If using **await d.preview()** throws a **libxcomposite.so.1 not found error**, execute the following commands:

.. code-block:: bash

    apt-get update
    apt-get install libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxtst6 libcups2 libxss1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0 libgtk-3-0 libgdk-pixbuf2.0-0


Download datasets
-----------------

1. Automatically download datasets
*************************

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
