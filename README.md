
# cuXfilter 
> `cuXfilter` is inspired from the Crossfilter library, which is a fast, browser-based filtering mechanism across multiple dimensions and offers features do groupby operations on top of the dimensions. One of the major limitations of using Crossfilter is that it keeps data in-memory on client-side in a browser, making it inefficient for processing large datasets. `cuXfilter` uses `cuDF` on the server-side, while keeping the dataframe in the GPU throughout the session. This results in sub-second response times for histogram calculations, groupby operations and querying datasets in the range of 10M to 200M rows(multiple columns).

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

while in the directory, run the following commands:

You can skip steps 1&2 if you do not wish to expose the `cuXfilter` demos on port 3004
1. edit the config.json file in the root directory
2. add your servel url to the `whitelisted_urls_for_clients` array in the format: `http://server.ip.addr:3004`
3. `docker build -t user_name/viz .`
4. `docker run --runtime=nvidia  -d -p 3000:3000 -p 3004:3004 --name rapids_viz -v /folder/with/data:/usr/src/app/node_server/uploads user_name/viz`


Access the crossfilter demos at `http://server.ip.addr:3004/demos/examples`


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

