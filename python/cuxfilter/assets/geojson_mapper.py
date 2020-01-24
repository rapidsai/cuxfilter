import json
from urllib.request import urlopen
import geopandas as gpd


def geo_json_mapper(url, prop=None, projection=3857):
    if "http" in url:
        data = urlopen(url).read().decode()
    else:
        try:
            data = open(url, "r").read()
        except Exception as e:
            raise ValueError("url invalid" + e)

    temp_gpd_df = gpd.read_file(data).to_crs(epsg=projection)

    if prop == "" or prop is None:
        if temp_gpd_df.columns[0] != 'geometry':
            prop = temp_gpd_df.columns[0]
        else:
            prop = temp_gpd_df.columns[1]

    temp_gpd_df = temp_gpd_df.dissolve(by=prop, as_index=False)

    data_json = json.loads(temp_gpd_df.to_json())
    x_range = (
        temp_gpd_df.geometry.bounds.minx.min(),
        temp_gpd_df.geometry.bounds.maxx.max(),
    )
    y_range = (
        temp_gpd_df.geometry.bounds.miny.min(),
        temp_gpd_df.geometry.bounds.maxy.max(),
    )

    geo_mapper = {}

    for i in data_json["features"]:
        temp_index = i["properties"][prop]
        # check if temp_index(str) is a number, if so, store it as float,
        # else str
        if temp_index.replace(".", "", 1).isdigit():
            temp_index = float(temp_index)
        # if i["geometry"]["type"] == "Polygon":
        #     geo_mapper[temp_index] = [i["geometry"]["coordinates"]]
        # else:
        geo_mapper[temp_index] = i["geometry"]["coordinates"]

    return geo_mapper, x_range, y_range
