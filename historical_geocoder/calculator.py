import pandas as pd
import geopandas as gpd
from utils.calculation import polygon_to_point

def calculate_point(data, projection_crs, geographic_crs):
    data = polygon_to_point.get_point_from_address(data, projection_crs)
    # Convert to geographic coordinates
    data = gpd.GeoDataFrame(data, geometry="geometry")
    data.crs = projection_crs
    data = data.to_crs(geographic_crs)
    data["X"] = data.loc[data["geometry"].notnull(), "geometry"].x
    data["Y"] = data.loc[data["geometry"].notnull(), "geometry"].y
    return data