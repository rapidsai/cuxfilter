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
1. Install jupyterlab dependencies

.. code-block:: bash

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz
    jupyter labextension install jupyterlab_bokeh

2.running the server

.. code-block:: bash

    #enter ip address without http://
    #current port is the port at which jupyterlab is running
    d.app(notebook_url='ip.addr:current_port')
    # OR for a separate web app
    d.show(notebook_url='ip.addr:current_port')

Troubleshooting
~~~~~~~~~~~~~~~

1. If the await d.preview() throws a libxcomposite.so.1 not found error, execute the following commands:

.. code-block:: bash

    apt-get update
    apt-get install libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxtst6 libcups2 libxss1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0 libgtk-3-0 libgdk-pixbuf2.0-0

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
    curl https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2015-01.csv --create-dirs -o ./nyc_taxi.csv
    curl https://s3.us-east-2.amazonaws.com/rapidsai-data/viz-data/146M_predictions_v2.arrow.gz --create-dirs -o ./146M_predictions_v2.arrow.gz
    curl https://s3.us-east-2.amazonaws.com/rapidsai-data/viz-data/auto_accidents.arrow.gz --create-dirs -o ./auto_accidents.arrow.gz

    python -c "from cuxfilter.sampledata import datasets_check; datasets_check(base_dir='./')"