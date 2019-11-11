import json
from urllib.request import urlopen
import geopandas as gpd

def geo_json_mapper(url, prop=None):
    try:
        data = urlopen(url).read().decode()
    except:
        data = open(url, 'r').read()
    temp_gpd_df = gpd.read_file(data)
    if temp_gpd_df.crs['init'] != 'epsg:3857':
        temp_gpd_df = temp_gpd_df.to_crs(epsg=3857)
    
    data_json = json.loads(temp_gpd_df.to_json())
    x_range = (temp_gpd_df.geometry.bounds.minx.min(), temp_gpd_df.geometry.bounds.maxx.max())
    y_range = (temp_gpd_df.geometry.bounds.miny.min(), temp_gpd_df.geometry.bounds.maxy.max())
    
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

    return geo_mapper, x_range, y_range