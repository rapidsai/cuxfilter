source activate cudf

# export sanic_ENV=production
# export sanic_APP=./sanic_server/run.py
# export LC_ALL=C.UTF-8
# export LANG=C.UTF-8

cudf_port=`cat config.json | jq --raw-output '.sanic_server_port_cudf_internal'`
pandas_port=`cat config.json | jq --raw-output '.sanic_server_port_pandas_internal'`
demos_serve_port_internal=3004

cd ./sanic_server
#cudf engine
# pm2 start "sanic run --port=$cudf_port" --watch
pm2 start "python -m sanic app.app --port=$cudf_port" --watch

#pandas engine
# pm2 start "sanic run --port=$pandas_port" --watch
pm2 start "python -m sanic app.app --port=$pandas_port" --watch

cd ../node_server
pm2 start npm -- start --watch

cd '../demos/GTC demo/'
npm run start &

cd ../../
pm2 serve --port=$demos_serve_port_internal

pm2 logs
#uncomment below two lines to run a jupyter notebook intance
#cd ../
#jupyter notebook --ip 0.0.0.0 --port 3004 --allow-root &
