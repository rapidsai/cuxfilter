source activate gdf
export FLASK_ENV=development
export FLASK_APP=../python_scripts/flask_server/run.py
flask run --port=3002
npm start
