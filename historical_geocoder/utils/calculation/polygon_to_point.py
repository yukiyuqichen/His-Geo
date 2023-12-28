import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, LinearRing, Point, Polygon


df_gcs = gpd.read_file("./data/2020China.geojson")

def get_polygon(projection_crs, code):
    df_pcs = df_gcs.to_crs(projection_crs)
    polygon_series = df_pcs.loc[df_pcs["CODE"] == code, "geometry"]
    polygon = polygon_series.iat[0]
    return polygon

def centroid(polygon):
    return polygon.centroid

def representative_point(polygon):
    return polygon.representative_point()

# intersection使用的都是centroid算法，不是representative_point算法
def intersection(polygon_series):
    centroids = []
    for polygon in polygon_series:
        centroids.append(polygon.centroid)
    if len(polygon_series) == 2:
        new_line = LineString(centroids)
        return new_line.centroid
    if len(polygon_series) > 2:
        # 如果使用三个点构建一个多边形，需要复制第一个点作为第四个点，以形成一个闭合的多边形
        centroids.append(centroids[0])
        new_polygon = Polygon(centroids).convex_hull
        return new_polygon.centroid

def get_x_max(geometry):
    if geometry.geom_type == 'Polygon':
        return max([coord[0] for coord in list(geometry.exterior.coords)])
    elif geometry.geom_type == 'MultiPolygon':
        # Handle MultiPolygon by iterating over each Polygon
        return max(coord[0] for polygon in geometry.geoms for coord in list(polygon.exterior.coords))

def get_x_min(geometry):
    if geometry.geom_type == 'Polygon':
        return min([coord[0] for coord in list(geometry.exterior.coords)])
    elif geometry.geom_type == 'MultiPolygon':
        # Handle MultiPolygon by iterating over each Polygon
        return min(coord[0] for polygon in geometry.geoms for coord in list(polygon.exterior.coords))

def get_y_max(geometry):
    if geometry.geom_type == 'Polygon':
        return max([coord[1] for coord in list(geometry.exterior.coords)])
    elif geometry.geom_type == 'MultiPolygon':
        # Handle MultiPolygon by iterating over each Polygon
        return max(coord[1] for polygon in geometry.geoms for coord in list(polygon.exterior.coords))

def get_y_min(geometry):
    if geometry.geom_type == 'Polygon':
        return min([coord[1] for coord in list(geometry.exterior.coords)])
    elif geometry.geom_type == 'MultiPolygon':
        # Handle MultiPolygon by iterating over each Polygon
        return min(coord[1] for polygon in geometry.geoms for coord in list(polygon.exterior.coords))


def horizontal_segment(polygon):
    y =  polygon.centroid.y
    x_max = get_x_max(polygon)
    x_min = get_x_min(polygon)
    y_max = get_y_max(polygon)
    y_min = get_y_min(polygon)
    line = LineString([(x_min, y), (x_max, y)])
    buffer_width_north = y_max - y
    buffer_width_south = y_min - y
    north_buffer = line.buffer(buffer_width_north, single_sided=True)
    south_buffer = line.buffer(buffer_width_south, single_sided=True)
    north_part = polygon.intersection(north_buffer)
    south_part = polygon.intersection(south_buffer)
    return north_part, south_part

def vertical_segment(polygon):
    x =  polygon.centroid.x
    x_max = get_x_max(polygon)
    x_min = get_x_min(polygon)
    y_max = get_y_max(polygon)
    y_min = get_y_min(polygon)
    line = LineString([(x, y_min), (x, y_max)])
    buffer_width_east = x_min - x
    buffer_width_west = x_max - x
    east_buffer = line.buffer(buffer_width_east, single_sided=True)
    west_buffer = line.buffer(buffer_width_west, single_sided=True)
    east_part = polygon.intersection(east_buffer)
    west_part = polygon.intersection(west_buffer)
    return east_part, west_part

def horizontal_and_vertical_segment(polygon):
    north_part, south_part = horizontal_segment(polygon)
    east_part, west_part = vertical_segment(polygon)
    northeast_part = north_part.intersection(east_part)
    northwest_part = north_part.intersection(west_part)
    southeast_part = south_part.intersection(east_part)
    southwest_part = south_part.intersection(west_part)
    return northeast_part, northwest_part, southeast_part, southwest_part

def with_direction(polygon, direction):
    if direction == "南":
        _, south_part = horizontal_segment(polygon)
        point = south_part.representative_point()
    if direction == "北":
        north_part, _ = horizontal_segment(polygon)
        point = north_part.representative_point()
    if direction == "西":
        _, west_part = vertical_segment(polygon)
        point = west_part.representative_point()
    if direction == "东":
        east_part, _ = vertical_segment(polygon)
        point = east_part.representative_point()
    if direction == "东南":
        _, _, southeast_part, _ = horizontal_and_vertical_segment(polygon)
        point = southeast_part.representative_point()
    if direction == "西南":
        _, _, _, southwest_part = horizontal_and_vertical_segment(polygon)
        point = southwest_part.representative_point()
    if direction == "东北":
        northeast_part, _, _, _ = horizontal_and_vertical_segment(polygon)
        point = northeast_part.representative_point()
    if direction == "西北":
        _, northwest_part, _, _ = horizontal_and_vertical_segment(polygon)
        point = northwest_part.representative_point()
    return point


def calculate_point(projection_crs, codes, point_type, direction):
    if point_type == "centroid":
        polygon = get_polygon(projection_crs, codes[0])
        point = centroid(polygon)
    if point_type == "representative_point":
        polygon = get_polygon(projection_crs, codes[0])
        point = representative_point(polygon)
    if point_type == "with_direction":
        polygon = get_polygon(projection_crs, codes[0])
        point = with_direction(polygon, direction)
    if point_type == "intersection":
        polygon_series = gpd.GeoSeries()
        for code in codes:
            polygon = get_polygon(projection_crs, code)
            polygon_series = pd.concat([polygon_series, gpd.GeoSeries([polygon])])
        point = intersection(polygon_series)
    return point


def get_point_from_address_row(row, projection_crs):
    codes = [list(i.values())[0] for i in row["Match Result"]]
    direction = row["Direction"]
    if len(row["Match Error"]) < 1:
        if row["Match Type"] == "Multiple":
            point_type = "intersection"
        elif row["Direction"] is not None:
            point_type = "with_direction"
        else:
            point_type = "representative_point"
        point = calculate_point(projection_crs, codes, point_type, direction)
        return point

    return None
    

def get_point_from_address(data, projection_crs):
    data["geometry"] = data.apply(lambda x: get_point_from_address_row(x, projection_crs), axis=1)
    return data