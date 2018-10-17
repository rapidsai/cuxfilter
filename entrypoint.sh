source activate gdf

export FLASK_ENV=development
export FLASK_APP=./flask_server/run.py
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

pygdf_port=`cat config.json | jq --raw-output '.flask_server_port_pygdf'`
pandas_port=`cat config.json | jq --raw-output '.flask_server_port_pandas'`

#pygdf engine
pm2 start "flask run --port=$pygdf_port"

#pandas engine
pm2 start "flask run --port=$pandas_port"

cd ./node_server
pm2 start npm -- start

pm2 logs
#uncomment below two lines to run a jupyter notebook intance
#cd ../
#jupyter notebook --ip 0.0.0.0 --port 3004 --allow-root &
