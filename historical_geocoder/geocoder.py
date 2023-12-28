import pandas as pd
import geopandas as gpd
import normalizer
import matcher
import detector
import calculator


class Geocoder:

    def __init__(self, addresses, lang="ch", projection_crs="EPSG:2333", geographic_crs="EPSG:4326", address_separator="-"):
        self.lang = lang
        self.projection_crs = projection_crs
        self.geographic_crs = geographic_crs
        self.address_separator = address_separator
        self.data = pd.DataFrame(addresses, columns=["Address"])
        self.data["Original Address"] = self.data["Address"]

        self.split_address()
        self.normalize_address()
    
    def split_address(self):
        """
        data["Address"] will be a list of multiple addresses after running split_address,
        even if there is only one address or there is no address separator.
        """
        if self.address_separator is not None:
            self.data["Address"] = self.data["Address"].apply(lambda x: x.split(self.address_separator))
        else:
            self.data["Address"] = self.data["Address"].apply(lambda x: [x])
        
        self.data["Match Type"] = self.data["Address"].apply(lambda x: "Multiple" if len(x) > 1 else "Single")

    def normalize_address(self):
        self.data["Address"] = self.data["Address"].apply(lambda x: [normalizer.normalize_address(i, structure_sign="/", lang=self.lang) for i in x])

    def match_address(self):
        self.data = matcher.match_address(self.data, self.lang)

    def detect_direction(self):
        self.data = detector.detect_direction(self.data)

    def calculate_point(self):
        self.data = calculator.calculate_point(self.data, self.projection_crs, self.geographic_crs)
        
        self.data["Address"] = self.data["Original Address"]
        try:
            self.data.drop(columns=["Original Address"], inplace=True)
        except:
            pass