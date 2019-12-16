Installation
============

NOTE: cuxfilter is in ongoing development and the installation instructions will be updated in the near future.


Install cuxfilter Nightly(0.12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    # for CUDA 9.2
    conda install -c rapidsai-nightly cuxfilter=0.12 cudatoolkit=9.2

    # or, for CUDA 10.0
    conda install -c rapidsai-nightly cuxfilter=0.12 cudatoolkit=10.0

To run the bokeh server in a jupyter lab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. expose an additional port for server, lets call it bokeh_port.
2. Install jupyterlab dependencies

.. code-block:: bash

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz
    jupyter labextension install jupyterlab_bokeh

3.running the server

.. code-block:: bash

    #enter ip address without http://
    #current port is the port at which jupyterlab is running
    d.app(url='ip.addr:current_port', port=bokeh_port)
    # OR for a separate web app
    d.show('ip.addr:bokeh_port')

Download datasets
-----------------

1. Auto download datasets

The notebooks inside `python/notebooks` already have a check function which verifies whether the example dataset is downloaded, and downloads it if it's not.

2. Download manually

While in the directory you want the datasets to be saved, execute the following

.. code-block:: bash

    #go the the environment where cuxfilter is installed. Skip if in a docker container
    source activate test_env

    #download and extract the datasets
    python -c "from cuxfilter.sampledata import datasets_check; datasets_check(base_dir='./')"


Individual links:

- Download the mortgage dataset  - https://s3.us-east-2.amazonaws.com/rapidsai-data/viz-data/146M_predictions_v2.arrow.gz

- Nyc taxi dataset - https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2015-01.csv

- Auto dataset - https://s3.us-east-2.amazonaws.com/rapidsai-data/viz-data/auto_accidents.arrow.gz