
# cuXfilter .js
**NOTE: current development is focusing on the python version**

A client-server architecture with a javascript api to do  cross-filtering viz dashboards powered by cudf.


### Table of Contents
- [Installation](#installation)
- [Architecture](#architecture)
    - [Server-side](#server-side)
    - [Client-side](#client-side)
- [Memory Limitations](#memory-limitations)
- [Troubleshooting](#troubleshooting)
- [File Conversion](#file-conversion)


## Installation


**To build using Docker:**


1. Edit the `config.env` file to reflect accurate IP, dataset name, and mapbox token values.
    1. add your server ip address to the `server_ip` property in the format: `http://server.ip.addr`
    2. add `demo_mapbox_token` for running the GTC demo
    3. download the dataset `146M_predictions_v2.arrow` from [here](https://rapidsai.github.io/demos/datasets)
3. `docker build -t user_name/viz .`
4. `docker run --runtime=nvidia  -d --env-file ./config.env -p 80:80 --name rapids_viz -v /folder/with/data:/usr/src/app/node_server/uploads user_name/viz`

Config.env Parameters:

1. `server_ip`: ip address of the server machine, needs to be set before building the docker container
2. `cuXfilter_port`: internal port at which cuXfilter server runs. No need to change this.*Do not publish this port*
3. `demos_serve_port`: internal port at which demos run. No need to change this.*Do not publish this port*
4. `gtc_demo_port`: internal port at which gtc demo server runs. No need to change this.*Do not publish this port*
5. `sanic_server_port_cudf`: sanic_server(cudf) runs on this port, internal to the container and can only be accessed by the node_server. *Do not publish this port*
6. `sanic_server_port_pandas`: sanic_server(pandas) runs on this port, internal to the container and can only be accessed by the node_server. *Do not publish this port*
7. `whitelisted_urls_for_clients`: list of whitelisted urls for clients to access node_server. User can add a list of urls(before building the container) he/she plans to develop on as origin, to avoid CORs issues.
8. `jupyter_port`: internal port at which jupyter notebook server runs. No need to change this.*Do not publish this port*
9. `demo_mapbox_token`: mapbox token for the mortgage demo. Can be created for free [here](https://www.mapbox.com/help/define-access-token/)
10. `demo_dataset_name`: dataset name for the example and mortgage demo. Default value: '146M_predictions_v2'. Can be downloaded from [here](https://rapidsai.github.io/demos/datasets)
11. `rmm`: using the experimental memory pool allocator(https://github.com/rapidsai/rmm) gives better performance, but may throw out of memory errors.


With the default settings:

Access the crossfilter demos at `http://server.ip.addr/demos/examples/`

Access the GTC demos at `http://server.ip.addr/demos/gtc_demo`

Access jupyter integration demo at `http://server.ip.addr/jupyter`


## Architecture
> **Docker container(python_sanic <--> node) SERVER  <<<===(socket.io)===>>> browser(client-side JS)**

![Architecture](./cuxfilter.png)

### Server-side
1. [Sanic server](sanic_server)

    > The sanic server interacts with the node_server, and maintains dataframe objects in memory, throughout the user session. There are two instances of the sanic_server running all the time, one at port 3002 (handling all cudf dataframe queries) and the other at port 3003 (handling all pandas dataframe queries, incase anyone wants to compare performance). This server is not exposed to the cuXfilter-client.js library, and is accessable only to the node-server, which acts as a load-balancer between cuXfilter-client.js library and the sanic server.

    Files:
    1. `app/views.py` -> handles all routes, and appends each response with calculation time
    2. `app/utilities/cuXfilter_utils.py` -> all cudf crossfilter functions
    3. `app/utilities/numbaHistinMem.py` -> histogram calculations using numba for a cudf.Series(ndarray)
    4. `app/utilities/pandas_utils.py` -> all pandas crossfilter functions



2. [Node server](node_server)

    > The Node server is exposed to the cuXfilter-client.js library and handles socket.io incoming requests and responses. It handles user-sessions, and gives an option to the client-side to perform cross-browser/cross-tab crossfiltering too.

    Files:
    1. `routes/cuXfilter.js` -> handles all socket-io routes, and appends each response with the amount of time spent by the node_server for each request
    2. `routes/utilities/cuXfilter_utils.js` -> utility functions for communicating with the sanic_server and handling the responses

### Client-side
1. [cuXfilter-client.js](client_side)

    > A javascript(es6) client library that provides crossfilter functionality to create interactive vizualizations right from the browser

    Documentation and examples can be found [here](client_side)



## Memory Limitations
Currently, there are a few memory limitations for running cuXfilter.

- Dataset size should be half the size of total GPU memory available. This is because the GPU memory usage spikes around 2X, in case of groupby operations.

>  This will not be an issue once dask_gdf engine is implemented(assuming the user has access to multiple GPUs)



## Troubleshooting
In case the server becomes unresponsive, here are the steps you can take to resolve it:

1. Check if the gpu memory is full, using the `nvidia-smi` command. If the gpu memory usage seems full and frozen, this may be due to the cudf out of memory error, which may happen if the dataset is too large to fit into the GPU memory. Please refer `Memory limitations` while choosing datasets

A docker container restart might solve the issue temporarily.



## File Conversion
Currently, cuXfilter supports only arrow file format as input. The `python_scripts` folder in the root directory provides a helper script to convert csv to arrow file. For more information, follow this [link](python_scripts)
