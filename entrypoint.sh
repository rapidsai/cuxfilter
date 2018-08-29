source activate gdf
export FLASK_ENV=development
export FLASK_APP=../python_scripts/flask_server/run.py
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
flask run --port=3002 &
cd ../nvidia-smi-gadget
npm start &
cd ../node_server
npm start
# ls
# cd ../
# jupyter notebook --ip 0.0.0.0 --port 3004 --allow-root &
