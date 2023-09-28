import cuspatial
from shapely.geometry import Polygon
import geopandas as gpd


def point_in_polygon(df, x, y, polygons):
    points = cuspatial.GeoSeries.from_points_xy(
        df[[x, y]].interleave_columns().astype("float64")
    )
    polygons = cuspatial.GeoSeries(
        gpd.GeoSeries(Polygon(polygons)), index=["selection"]
    )
    return cuspatial.point_in_polygon(points, polygons)
