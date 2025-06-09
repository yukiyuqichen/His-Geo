import pandas as pd
import os
from .utils.normalization import normalization_ch_modern as normalizer_ch_modern
from .utils.normalization import normalization_ch_his as normalizer_ch_his
from .utils.matching import hierarchical_matching_ch_modern as matcher_ch_modern
from .utils.matching import hierarchical_matching_ch_his as matcher_ch_his

current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
county_ch_modern = os.path.join(current_directory, 'data/Modern', 'ModernChinaCountyTable.csv')
tgaz_ch_historic = os.path.join(current_directory, 'data/Historic', 'tgaz_chgis.csv')
gazetteer_ch_historic = os.path.join(current_directory, 'data/Historic', 'gazetteer_chgis.csv')

def match_address(data, lang, preferences, year_range):
    if lang == "ch":
        data["Match Elements"], data["Match Result"], data["Match Level"], data["Match Error"], data["Match Period"], data["geometry"] = None, None, None, None, None, None
        for preference in preferences:
            if preference == "modern":
                county_table = pd.read_csv(county_ch_modern, encoding="utf-8-sig")
                county_table_unnormalized = county_table.copy()
                county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']] = county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']].applymap(normalizer_ch_modern.normalize_address, structure_sign="")
                level_dict = {0: None, 1: "Province", 2: "Prefecture", 3: "County"}
                data = matcher_ch_modern.match_address(data, county_table, county_table_unnormalized, level_dict)
            if preference == "historic":
                tgaz = pd.read_csv(tgaz_ch_historic, encoding="utf-8-sig")
                gazetteer = pd.read_csv(gazetteer_ch_historic, encoding="utf-8-sig")
                gazetteer_unnormalized = gazetteer.copy()
                gazetteer[['LEV1_NAME', 'LEV2_NAME', 'LEV3_NAME', 'LEV4_NAME', 'LEV5_NAME']] = gazetteer[['LEV1_NAME', 'LEV2_NAME', 'LEV3_NAME', 'LEV4_NAME', 'LEV5_NAME']].applymap(normalizer_ch_his.normalize_address, structure_sign="")
                level_dict = {0: None, 1: "LEV1", 2: "LEV2", 3: "LEV3", 4: "LEV4", 5: "LEV5"}
                data = matcher_ch_his.match_address(data, gazetteer, gazetteer_unnormalized, level_dict, year_range)

    return data
        

