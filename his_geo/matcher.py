import pandas as pd
import os
from .utils.normalization import normalization_ch as normalizer_ch
from .utils.matching import hierarchical_matching_ch_modern as matcher_ch_modern
from .utils.matching import hierarchical_matching_ch_his as matcher_ch_his

current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
database_ch_modern = os.path.join(current_directory, 'data/Modern', 'ModernChinaCountyTable.csv')
database_ch_historic = os.path.join(current_directory, 'data/Historic', 'v6_time_cnty_pts_gbk_wgs84.csv')

def match_address(data, lang, preferences):
    if lang == "ch":
        data["Match Elements"], data["Match Result"], data["Match Level"], data["Match Error"], data["Match Period"], data["geometry"] = None, None, None, None, None, None
        for preference in preferences:
            if preference == "modern":
                county_table = pd.read_csv(database_ch_modern, encoding="utf-8-sig")
                county_table_unnormalized = county_table.copy()
                county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']] = county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']].applymap(normalizer_ch.normalize_address, structure_sign="")
                level_dict = {0: None, 1: "Province", 2: "Prefecture", 3: "County"}
                data = matcher_ch_modern.match_address(data, county_table, county_table_unnormalized, level_dict)
            if preference == "historic":
                county_table = pd.read_csv(database_ch_historic, encoding="utf-8-sig")
                level_dict = {0: None, 1: "Province", 2: "Prefecture", 3: "County"}
                data = matcher_ch_his.match_address(data, county_table, level_dict)

    return data
        

