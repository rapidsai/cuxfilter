from urllib.request import urlopen
import geopandas as gpd
import pandas as pd


def geo_json_mapper(
    url, prop=None, projection=3857, column_x=None, column_x_dtype="float32"
):
    if "http" in url:
        data = urlopen(url).read().decode()
    else:
        try:
            data = open(url, "r").read()
        except Exception as e:
            raise ValueError("url invalid" + e)

    temp_gpd_df = gpd.read_file(data).to_crs(epsg=projection)

    df = pd.read_json(temp_gpd_df.to_json())

    x_range = (
        temp_gpd_df.geometry.bounds.minx.min(),
        temp_gpd_df.geometry.bounds.maxx.max(),
    )
    y_range = (
        temp_gpd_df.geometry.bounds.miny.min(),
        temp_gpd_df.geometry.bounds.maxy.max(),
    )

    if prop == "" or prop is None:
        prop = list(df["features"][0]["properties"].keys())[0]

    geo_mapper = pd.DataFrame()

    geo_mapper["coordinates"] = df["features"].apply(
        lambda row: row["geometry"]["coordinates"]
    )
    geo_mapper["__geo_type__"] = df["features"].apply(
        lambda row: row["geometry"]["type"]
    )

    def kernel(row):
        if row["__geo_type__"] == "MultiPolygon":
            temp_list = []
            for i in row["coordinates"]:
                temp_list.append(i[0])
            row["coordinates"] = temp_list
        elif row["__geo_type__"] == "Polygon":
            row["coordinates"] = row["coordinates"][0]
        return row

    geo_mapper = geo_mapper.apply(kernel, axis=1).drop(
        columns=["__geo_type__"]
    )

    if column_x is None:
        column_x = prop

    geo_mapper[column_x] = (
        df["features"]
        .apply(lambda row: row["properties"][prop])
        .astype(column_x_dtype)
    )

    return geo_mapper, x_range, y_range
