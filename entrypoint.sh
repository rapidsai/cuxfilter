#activating the conda environment
source activate cudf

cd ./sanic_server
#cudf engine
pm2 start "python -m sanic app.app --port=$sanic_server_port_cudf" --watch

#pandas engine
pm2 start "python -m sanic app.app --port=$sanic_server_port_pandas" --watch

#cuxfilter engine
cd ../node_server
pm2 start npm -- start --watch

#gtc demo
cd '../demos/GTC demo/'
pm2 start "npm start --port=$gtc_demo_port" --watch

#jupyter notebook server
cd ../Jupyter_Integration
jupyter notebook --ip 0.0.0.0 --port $jupyter_port --allow-root --NotebookApp.token='' --NotebookApp.base_url='/jupyter' &

#starting nginx reverse-proxying
service nginx start

#genrating all server logs
pm2 logs
