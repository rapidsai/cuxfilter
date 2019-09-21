Installation
============


Steps
-----

1. Clone the repositories

.. code-block:: bash
    
    git clone https://github.com/rapidsai/cuxfilter
    git clone https://github.com/rapidsai/cudatashader


2. If you want to install it in an isolated environment

.. code-block:: bash

    conda create -n test_env
    source activate test_env

3. Install dependencies

.. code-block:: bash

    cd cuxfilter_refactor
    make

4. Install cuXfilter-py, while in the cuxfilter_refactor folder

.. code-block:: bash

    pip install -e .

5. Install cuDatashader

.. code-block:: bash    

    cd ../cuviz
    pip install -e .

6. Start notebook or jupyter lab

.. code-block:: bash    

    jupyter notebook / jupyter lab


Troubleshooting
----------------

Running in a remote jupyter lab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. expose an additional port for server, lets call it bokeh_port. 

2. Install jupyterlab dependencies

.. code-block:: bash

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz
    jupyter labextension install jupyterlab_bokeh


3. running the server

.. code-block:: python

    #enter ip address without http://
    #current port is the port at which jupyterlab is running
    d.app(url='ip.addr:current_port', port=bokeh_port)


Running in a remote jupyter notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. expose an additional port for server, lets call it bokeh_port. 

2. running the server

.. code-block:: python

    #enter ip address without http://
    #current port is the port at which jupyter notebook is running
    d.app(url='ip.addr:current_port', port=bokeh_port)


Download datasets
-----------------

- Download the mortgage dataset from [here](https://docs.rapids.ai/datasets/mortgage-viz-data)

- Nyc taxi dataset from [here](https://drive.google.com/file/d/1mTvl66VLzHwQJPcgnGBdmZTNEdNp1tYo/view?usp=sharing)

- Auto dataset from [here](https://drive.google.com/file/d/1jxySYJ9e32hI8PQ5QPr9_xrsu37N5fOM/view?usp=sharing)
