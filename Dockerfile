FROM cudf

WORKDIR /usr/src/app

RUN conda install -n cudf -y -c conda-forge jupyter flask

RUN apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -yq curl && curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -yq nodejs build-essential jq && \
    npm update -g npm && \
    rm -rf /var/lib/apt/lists/*

COPY . .

WORKDIR /usr/src/app/node_server
RUN mkdir uploads && npm install && npm install -g pm2

WORKDIR '/usr/src/app/demos/GTC demo'
RUN npm install

WORKDIR /usr/src/app
ENTRYPOINT ["bash","./entrypoint.sh"]
