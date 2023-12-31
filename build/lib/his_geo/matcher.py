import pandas as pd
import os
from .utils.normalization import normalization_ch as normalizer_ch
from .utils.matching import hierarchical_matching_ch as matcher_ch

current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
database_file_path_ch = os.path.join(current_directory, 'data', '2020ChinaCountyTable.csv')


def match_address(data, lang):
    if lang == "ch":
        county_table = pd.read_csv(database_file_path_ch, encoding="utf-8-sig")
        county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']] = county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']].applymap(normalizer_ch.normalize_address, structure_sign="")
        level_dict = {0: None, 1: "Province", 2: "City", 3: "County"}
        data = matcher_ch.match_address(data, county_table, level_dict)

    return data
        

