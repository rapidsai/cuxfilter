source activate cudf

export FLASK_ENV=development
export FLASK_APP=./flask_server/run.py
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

cudf_port=`cat config.json | jq --raw-output '.flask_server_port_cudf_internal'`
pandas_port=`cat config.json | jq --raw-output '.flask_server_port_pandas_internal'`
demos_serve_url=`cat config.json | jq --raw-output '.demos_serve_port_internal'`

#cudf engine
pm2 start "flask run --port=$cudf_port" --watch

#pandas engine
pm2 start "flask run --port=$pandas_port" --watch

cd ./node_server
pm2 start npm -- start --watch

cd './demos/GTC demo'
pm2 start npm -- start

cd ../
pm2 serve --port=$demos_serve_url

pm2 logs
#uncomment below two lines to run a jupyter notebook intance
#cd ../
#jupyter notebook --ip 0.0.0.0 --port 3004 --allow-root &
