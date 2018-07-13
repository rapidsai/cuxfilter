FROM node:8

WORKDIR /usr/src/app

# Install conda
ADD https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh /miniconda.sh
RUN sh /miniconda.sh -b -p /conda && /conda/bin/conda update -n base conda
ENV PATH=${PATH}:/conda/bin

COPY . .

WORKDIR /usr/src/app/node-server
RUN pwd


RUN mkdir uploads 
RUN npm install

EXPOSE 3000

CMD ["npm","start"]

