
# cuXfilter
> `cuXfilter` is inspired from the Crossfilter library, which is a fast, browser-based filtering mechanism across multiple dimensions and offers features do groupby operations on top of the dimensions. One of the major limitations of using Crossfilter is that it keeps data in-memory on a client-side browser, making it inefficient for processing large datasets. `cuXfilter` uses `cuDF` on the server-side, while keeping the dataframe in the GPU throughout the session. This results in sub-second response times for histogram calculations, groupby operations and querying datasets in the range of 10M to 200M rows (multiple columns).

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

Edit the `config.json` file to reflect accurate IP, dataset name, and mapbox token values. While in the directory, run the following commands:

1. edit the config.json file in the root directory
2. add your server ip address to the `server_ip` property in the format: `http://server.ip.addr`
3. `docker build -t user_name/viz .`
4. `docker run --runtime=nvidia  -d -p 3000:3000 -p 3004:3004 -p 3005:3005 --name rapids_viz -v /folder/with/data:/usr/src/app/node_server/uploads user_name/viz`

Config.json Parameters:

1. `server_ip`: ip address of the server machine, needs to be set before building the docker container
2. `cuXfilter_port_external`: port on which the cuXfilter api can be accessed externally outside the docker container, default is `3000`. (Internally cuXfilter runs on port `3000`). Port needs to be published while running the container(`-p 3000:3000`).
3. `demos_serve_port_external`: port on which examples are to be served externally, default is `3004`.(Internally demos are served on port `3004`). Port needs to be published while running the container(`-p 3004:3004`).
4. `gtc_demo_port_external`: port on which mortgage demo is served externally, default is `3005`. (Internally mortgage demo runs on port `3005`) Port needs to be published while running the container(`-p 3005:3005`).
5. `flask_server_port_cudf_internal`: flask_server(cudf) runs on this port, internal to the container and can only be accessed by the node_server. *Do not publish this port*
6. `flask_server_port_pandas_internal`: flask_server(pandas) runs on this port, internal to the container and can only be accessed by the node_server. *Do not publish this port*
7. `whitelisted_urls_for_clients`: list of whitelisted urls for clients to access node_server. User can add a list of urls(before building the container) he/she plans to develop on as origin, to avoid CORs issues.
8. `demo_mapbox_token`: mapbox token for the mortgage demo. Can be created for free [here](https://www.mapbox.com/help/define-access-token/)
9. `demo_dataset_name`: dataset name for the example and mortgage demo. Default value: '146M_predictions_v2'. Can be downloaded from [here](https://drive.google.com/open?id=12HiPwoxmmLsWhQHQMgyzxTk4za_Y7XRh)


With the defualt settings:

Access the crossfilter demos at `http://server.ip.addr:3004/demos/examples/index.html`

Access the GTC demos at `http://server.ip.addr:3005/`


## Architecture
> **Docker container(python_flask <--> node) SERVER  <<<===(socket.io)===>>> browser(client-side JS)**

### Server-side
1. [Flask server](flask_server)

    > The flask server interacts with the node_server, and maintains dataframe objects in memory, throughout the user session. There are two instances of the flask_server running all the time, one at port 3002 (handling all cudf dataframe queries) and the other at port 3003 (handling all pandas dataframe queries, incase anyone wants to compare performance). This server is not exposed to the cuXfilter-client.js library, and is accessable only to the node-server, which acts as a load-balancer between cuXfilter-client.js library and the flask server.

    Files:
    1. `app/views.py` -> handles all routes, and appends each response with calculation time
    2. `app/utilities/cuXfilter_utils.py` -> all cudf crossfilter functions
    3. `app/utilities/numbaHistinMem.py` -> histogram calculations using numba for a cudf.Series(ndarray)
    4. `app/utilities/pandas_utils.py` -> all pandas crossfilter functions



2. [Node server](node_server)

    > The Node server is exposed to the cuXfilter-client.js library and handles socket.io incoming requests and responses. It handles user-sessions, and gives an option to the client-side to perform cross-browser/cross-tab crossfiltering too.

    Files:
    1. `routes/cuXfilter.js` -> handles all socket-io routes, and appends each response with the amount of time spent by the node_server for each request
    2. `routes/utilities/cuXfilter_utils.js` -> utility functions for communicating with the flask_server and handling the responses

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
