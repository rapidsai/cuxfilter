source activate gdf
export FLASK_ENV=development
export FLASK_APP=../flask_server/run.py
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

#pygdf engine
flask run --port=3002 &

#pandas engine
flask run --port=3003 &

cd ../node_server
npm start


#uncomment below two lines to run a jupyter notebook intance
#cd ../
#jupyter notebook --ip 0.0.0.0 --port 3004 --allow-root &
