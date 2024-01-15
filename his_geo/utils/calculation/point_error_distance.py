import pandas as pd
import geopandas as gpd
from shapely.ops import nearest_points
from geopy.distance import geodesic


def compute_error_distance_row(row, gdf_database):
    target_point = row["geometry"]
    if target_point == None:
        return None
    else:
        valid_geometry = gdf_database["geometry"].is_valid
        gdf_database = gdf_database[valid_geometry]
        gdf_database_filtered = gdf_database[gdf_database["geometry"] != target_point].copy()
        nearest_point = nearest_points(target_point, gdf_database_filtered.unary_union)[1]
        distance = geodesic((target_point.y, target_point.x), (nearest_point.y, nearest_point.x)).kilometers
        return distance

def compute_error_distance(data, geographic_crs, gdf_database, lang):
    data["id"] = data.index
    data_filtered = data[data["Match Period"] == "historic"].copy()
    data_remaining = data[data["Match Period"] != "historic"].copy()
    data_filtered["Maximum Error Distance"] = data_filtered.apply(lambda row: compute_error_distance_row(row, gdf_database), axis=1)
    if lang == "ch":
        max_distance = 5046.768
    data_filtered["Certainty"] = data_filtered["Maximum Error Distance"].apply(lambda x: 1 - x / max_distance)
    data = pd.concat([data_remaining, data_filtered]).set_index("id").sort_index()
    return data