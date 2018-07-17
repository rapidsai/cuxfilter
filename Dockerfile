FROM pygdf

WORKDIR /usr/src/app

# Python packages from conda
#RUN conda install -n gdf -y \
#	pandas \
#	pyarrow \
#	numba \
#	cudatoolkit
RUN source activate gdf && conda install -c conda-forge pyarrow jupyter

RUN apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -yq curl

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -yq nodejs build-essential

# fix npm - not the latest version installed by apt-get
RUN npm install -g npm

COPY . .

WORKDIR /usr/src/app/node-server
RUN pwd

RUN mkdir uploads 
RUN npm install

EXPOSE 3000

#RUN source activate gdf
#CMD ["npm","start"]
