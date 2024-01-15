import os
import pandas as pd
import geopandas as gpd
from keplergl import KeplerGl
import json
from . import normalizer
from .import matcher
from .import detector
from .import calculator


class Geocoder:

    def __init__(self, addresses, lang="ch", preferences=['modern', 'historic'], geographic_crs="EPSG:4326", if_certainty=True):
        self.lang = lang
        self.preferences = preferences
        self.geographic_crs = geographic_crs
        self.if_certainty = if_certainty
        self.data = pd.DataFrame([str(i) for i in addresses], columns=["Address"])
        self.data["Address"] = self.data["Address"].apply(lambda x: [str(x)])
        self.data["Original Address"] = self.data["Address"]
        print("Initialization finished.")

    def detect_direction(self):
        self.data = detector.detect_direction(self.data, self.lang)
        print("Detection finished.")

    def match_address(self):
        self.data = matcher.match_address(self.data, self.lang, self.preferences)
        print("Matching finished.")

    def calculate_point(self):
        self.data = calculator.calculate_point(self.data, self.geographic_crs, self.lang, self.preferences, self.if_certainty)
        
        self.data["Address"] = self.data["Original Address"]
        try:
            self.data.drop(columns=["Original Address"], inplace=True)
        except:
            pass
        print("Calculation finished.")
    
    def visualize(self, crs=""):
        self.data = gpd.GeoDataFrame(self.data, geometry="geometry")
        self.data.crs = self.geographic_crs
        if crs != "":
            self.data = self.data.to_crs(crs)
        map = KeplerGl(height=500)
        map.add_data(data=self.data.dropna(subset=["geometry"]))

        return map