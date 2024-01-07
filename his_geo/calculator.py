import pandas as pd
import os
import geopandas as gpd
from .utils.calculation import polygon_to_point

current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
gdf_database_file_path_ch = os.path.join(current_directory, 'data', '2020China.geojson')

def calculate_point(data, geographic_crs, lang):
    if lang == "ch":
        gdf_database = gpd.read_file(gdf_database_file_path_ch, driver="GeoJSON")
    data = polygon_to_point.get_point_from_address(data, geographic_crs, gdf_database)
    data = gpd.GeoDataFrame(data, geometry="geometry")
    data["X"] = data.loc[data["geometry"].notnull(), "geometry"].x
    data["Y"] = data.loc[data["geometry"].notnull(), "geometry"].y
    return data