FROM rapidsai/rapidsai

WORKDIR /usr/src/app

RUN source activate gdf && conda install -c conda-forge pyarrow jupyter flask && \
    apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -yq curl && curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -yq nodejs build-essential jq && \
    npm update -g npm && \
    rm -rf /var/lib/apt/lists/*

COPY . .

WORKDIR /usr/src/app/node_server

RUN mkdir uploads && npm install && npm install -g pm2

WORKDIR /usr/src/app
ENTRYPOINT ["bash","./entrypoint.sh"]
