import pandas as pd
import utils.normalization.normalization_ch as normalizer_ch
import utils.matching.hierarchical_matching_ch as matcher_ch

def match_address(data, lang):
    if lang == "ch":
        county_table = pd.read_csv("./data/2020ChinaCountyTable.csv", encoding="utf-8-sig")
        county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']] = county_table[['PROV_CH', 'CITY_CH', 'COUNTY_CH']].applymap(normalizer_ch.normalize_address, structure_sign="")
        level_dict = {0: None, 1: "Province", 2: "City", 3: "County"}
        data = matcher_ch.match_address(data, county_table, level_dict)

    return data
        

