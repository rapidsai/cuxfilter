ARG CUDA_VERSION=9.2
ARG LINUX_VERSION=ubuntu16.04
FROM nvidia/cuda:${CUDA_VERSION}-devel-${LINUX_VERSION}

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/lib
# Needed for cugdf.concat(), avoids "OSError: library nvvm not found"
ENV NUMBAPRO_NVVM=/usr/local/cuda/nvvm/lib64/
ENV NUMBAPRO_LIBDEVICE=/usr/local/cuda/nvvm/libdevice/

ARG CC=5
ARG CXX=5
RUN apt update -y --fix-missing && \
    apt upgrade -y && \
    apt install -y \
      git \
      gcc-${CC} \
      g++-${CXX} \
      libboost-all-dev


# Install conda
ADD https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh /miniconda.sh
RUN sh /miniconda.sh -b -p /conda && /conda/bin/conda update -n base conda
ENV PATH=${PATH}:/conda/bin
# Enables "source activate conda"
SHELL ["/bin/bash", "-c"]

# Build cuDF conda env
ARG PYTHON_VERSION=3.6
RUN conda create -n cudf python=${PYTHON_VERSION}

WORKDIR /usr/src/app

ARG NUMBA_VERSION>=0.40.0
ARG NUMPY_VERSION>=1.14.3
ARG PANDAS_VERSION>=0.23.4
ARG FLASK_VERSION=1.0.2
 #pyarrow 0.12.0 for cudf=0.5.0
ARG PYARROW_VERSION=0.12.1
ARG SANIC_VERSION=0.8.3
RUN conda install -n cudf -c numba -c conda-forge -c rapidsai -c nvidia -c defaults cudf=0.7.0 jupyter \
      flask=${FLASK_VERSION} \
      sanic=${SANIC_VERSION} \
      numba=${NUMBA_VERSION} \
      numpy=${NUMPY_VERSION} \
      pandas=${PANDAS_VERSION} \
      pyarrow=${PYARROW_VERSION} \
      nvstrings \
      cmake

RUN apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -yq curl && curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -yq nodejs build-essential jq && \
    apt-get install -yq nginx && \
    npm update -g npm && \
    rm -rf /var/lib/apt/lists/*

COPY ./default /etc/nginx/sites-enabled/

RUN npm install npm@latest -g

COPY . .

WORKDIR /usr/src/app/node_server
RUN mkdir uploads && npm install && npm install -g pm2

WORKDIR /usr/src/app/client_side/library_src
RUN npm install && npm run build

WORKDIR /usr/src/app/demos/GTC\ demo
RUN npm install && npm run build

WORKDIR /usr/src/app
ENTRYPOINT ["bash","./entrypoint.sh"]
