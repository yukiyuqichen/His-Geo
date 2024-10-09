import pandas as pd
import os
import geopandas as gpd
from .utils.calculation import point_to_point, polygon_to_point

current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
gdf_database_ch_modern = os.path.join(current_directory, 'data/Modern', '2020China.geojson')
gdf_database_ch_historic = os.path.join(current_directory, 'data/Historic', 'tgaz_chgis.csv')

def calculate_point(data, geographic_crs, lang, preferences, if_certainty):
    if lang == "ch":
        for preference in preferences:
            if preference == "modern":
                print("Calculating modern location references...")
                gdf_database = gpd.read_file(gdf_database_ch_modern, driver="GeoJSON")
                data = polygon_to_point.get_point_from_address(data, geographic_crs, gdf_database, lang, if_certainty)
            if preference == "historic":
                print("Calculating historic location references...")
                df_database = pd.read_csv(gdf_database_ch_historic, encoding="utf-8-sig")
                gdf_database = gpd.GeoDataFrame(df_database, geometry=gpd.points_from_xy(df_database["X"], df_database["Y"]))
                data = point_to_point.get_point(data, gdf_database)
                if if_certainty == True:
                    data = point_to_point.compute_error_distance(data, geographic_crs, gdf_database, lang)
        try:
            data = gpd.GeoDataFrame(data, geometry="geometry")
            data["X"] = data.loc[data["geometry"].notnull(), "geometry"].x
            data["Y"] = data.loc[data["geometry"].notnull(), "geometry"].y
        except Exception as e:
            print(e)         
        
        try:
            data.drop(columns=["id"], inplace=True)
        except:
            pass

        return data