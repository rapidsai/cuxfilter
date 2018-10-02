source activate gdf
export FLASK_ENV=development
export FLASK_APP=../flask_server/run.py
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

#pygdf engine
flask run --port=3002 &

#pandas engine
flask run --port=3003 &


# uncomment the below 4 lines if you want to run the nvidia-smi gadget for the front-end
cd ../nvidia-smi-gadget
npm start &
cd ../node_server
npm start


#cd ../
#jupyter notebook --ip 0.0.0.0 --port 3004 --allow-root &
