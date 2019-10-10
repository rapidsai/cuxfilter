Installation
============

Note: You need to have RAPIDS (cudf) installed for cuXfilter to work


1. Installing in a rapids docker container
------------------------------------------

.. code-block:: bash

    Before you start juypter lab, you need to install cuxfilter and cudatashader.  In terminal, when you start docker, please run the following commands:

    #Get to the /rapidsai folder, up one level, where the libraries live.  List files to verify (you'll see cuspatal, cuml, cdf, etc)
    cd /rapids

    #Clone cuxfilter here
    git clone https://github.com/rapidsai/cuxfilter

    #Drop into cuxfilter's python library folder, make, and install
    cd cuxfilter/python
    make
    pip install -e .

    #Get back to /rapidsai folder
    cd /rapids

    #clone cudatashader
    git clone https://github.com/rapidsai/cudatashader

    Drop into cudatashader folder and install
    cd cudatashader
    pip install -e .

    # start a jupyter lab environment
    jupyter lab

    #To run the bokeh server in a jupyter lab

    : '
    1. expose an additional port for server, lets call it bokeh_port.
    2. Install jupyterlab dependencies
    '
    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz
    jupyter labextension install jupyterlab_bokeh

    : '
    3.running the server
    '
    #enter ip address without http://
    #current port is the port at which jupyterlab is running
    d.app(url='ip.addr:current_port', port=bokeh_port)
    # OR for a separate web app
    d.show('ip.addr:bokeh_port')



2. If installing in a conda environment
---------------------------------------

.. code-block:: bash

    #Clone cuxfilter here
    git clone https://github.com/rapidsai/cuxfilter

    #create a conda environment
    conda create -n test_env
    source activate test_env


    #Drop into cuxfilter's python library folder, make, and install
    cd cuxfilter/python
    make
    pip install -e .

    #Get back to /rapidsai folder
    cd ..
    cd ..

    #clone cudatashader
    git clone https://github.com/rapidsai/cudatashader

    Drop into cudatashader folder and install
    cd cudatashader
    pip install -e .


Download datasets
-----------------

1. Auto download datasets

The notebooks inside `python/notebooks` already have a check function which verifies whether the example dataset is downloaded, and downloads it if it's not.

2. Download manually

While in the directory you want the datasets to be saved, execute the following

.. code-block:: bash

    #go the the environment where cuXfilter is installed. Skip if in a docker container
    source activate test_env

    #download and extract the datasets
    python -c "from cuXfilter.sampledata import datasets_check; datasets_check(base_dir='./')"


Individual links:

- Download the mortgage dataset  - https://s3.us-east-2.amazonaws.com/rapidsai-data/viz-data/146M_predictions_v2.arrow.gz

- Nyc taxi dataset - https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2015-01.csv

- Auto dataset - https://s3.us-east-2.amazonaws.com/rapidsai-data/viz-data/auto_accidents.arrow.gz