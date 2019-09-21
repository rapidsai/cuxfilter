import json
from urllib.request import urlopen

def geo_json_mapper(url, prop=None):
    data = urlopen(url).read().decode()
    data_json = json.loads(data)
    if prop == '' or prop is None:
        prop = list(data_json['features'][0]['properties'].keys())[0]

    geo_mapper = {}

    for i in data_json['features']:
        temp_index = i['properties'][prop]
        #check if temp_index(str) is a number, if so, store it as float, else str
        if temp_index.replace('.','',1).isdigit():
            temp_index = float(temp_index)
        if i['geometry']['type'] == 'Polygon':
            geo_mapper[temp_index] = [i['geometry']['coordinates']]
        else:
            geo_mapper[temp_index] = i['geometry']['coordinates']

    return geo_mapper