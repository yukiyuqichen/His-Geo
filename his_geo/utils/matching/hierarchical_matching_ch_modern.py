import pandas as pd
import itertools


def generate_n_grams_chinese(text):
    """ Generate n-grams from a given Chinese text for all n from 2 to the length of text. """
    max_n = len(text)
    n_grams = []
    for n in range(2, max_n + 1):
        for i in range(len(text) - n + 1):
            n_gram = text[i:i + n]
            n_grams.append(n_gram)
    
    return n_grams

def check_elements_in_string(elements, string):
    temp_string = string
    for element in elements:
        if element in temp_string:
            temp_string = temp_string.replace(element, '', 1)
        else:
            return False
    return True

def match_address_row(row, county_table, level_dict):
    """
    Input: 
           row is a row of the dataframe
           row["Address"] is the addresses to be matched
    Return: 
            match_level is a str (None, "Province", "Prefecture", "County")
            match_final is a list of the most accurate codes
            match_errors is a list of errors ("No Match", "Multiple Matches")
            match_type is a str ("Single Location Reference", "Multiple Location References")
    """
    addresses = row["Address"]
    match_dataframe = pd.DataFrame(columns=["id", "element", "match_num"])
    match_elements = []
    match_final = []
    match_errors = []
    match_period = None

    print(addresses)
    
    for address in addresses:
        for i in range(len(county_table)):
            match_results_id = {}
            match_results_element = []
            address_temp = address
            province_name = county_table.loc[i, "PROV_CH"]
            if province_name in address_temp:
                match_results_element.append(province_name)
                match_results_id["province"] = county_table.loc[i, "PCODE"]
                address_temp = address_temp.replace(province_name, "")

            city_name = county_table.loc[i, "CITY_CH"]
            if city_name in address_temp:
                match_results_element.append(city_name)
                match_results_id["prefecture"] = county_table.loc[i, "DCODE"]
                address_temp = address_temp.replace(city_name, "")

            county_name = county_table.loc[i, "COUNTY_CH"]
            if county_name in address_temp:
                match_results_element.append(county_name)
                match_results_id["county"] = county_table.loc[i, "CODE2020"]
                address_temp = address_temp.replace(county_name, "")

            if len(match_results_id) > 0:
                new_row = {"id": match_results_id,
                        "element": match_results_element,
                        "match_num": len(match_results_id)}
                match_dataframe.loc[len(match_dataframe)] = new_row

        match_dataframe = match_dataframe.drop_duplicates(subset=["element"]).reset_index(drop=True)

        if len(match_dataframe) == 0:
            match_level = 0
            match_errors.append("No Match")

        elif len(match_dataframe) == 1:
            match = match_dataframe.iloc[0]
            match_elements.append(match["element"])
            if "county" in match["id"].keys():
                match_final.append({"county": match["id"]["county"]})
                match_level = 3
            elif "prefecture" in match["id"].keys():
                match_final.append({"prefecture": match["id"]["prefecture"]})
                match_level = 2
            elif "province" in match["id"].keys():
                match_final.append({"province": match["id"]["province"]})
                match_level = 1
            match_period = "modern"

        else:
            match_num_max = match_dataframe["match_num"].max()
            match_max = match_dataframe[match_dataframe["match_num"] == match_num_max].reset_index(drop=True).copy()
            if len(match_max) > 1:
                match_max["element_length"] = match_max["element"].apply(lambda x: len("".join(list(itertools.chain(*x)))))
                match_max = match_max[match_max["element_length"] == match_max["element_length"].max()]
                if len(match_max) > 1:
                    match_errors.append("Multiple Matches")

            for id, match in match_max.iterrows():
                match_elements.append(match["element"])    
                if "county" in match["id"].keys():
                    match_final.append({"county": match["id"]["county"]})
                    match_level = 3
                elif "prefecture" in match["id"].keys():
                    match_final.append({"prefecture": match["id"]["prefecture"]})
                    match_level = 2
                elif "province" in match["id"].keys():
                    match_final.append({"province": match["id"]["province"]})
                    match_level = 1

            match_period = "modern"

    match_level = level_dict[match_level]
    print(match_elements, match_final, match_level, match_errors, match_period)

    return match_elements, match_final, match_level, match_errors, match_period


def address_structuralize_row(match_results, county_table_unnormalized):

    codes = [list(i.values())[0] for i in match_results]

    provinces = []
    prefectures = []
    counties = []

    for code in codes:
    
        num = len(str(code))

        if num == 2:
            query = f"PCODE == {code}"
        elif num == 4:
            query = f"DCODE == {code}"
        elif num == 6:
            query = f"CODE2020 == {code}"

        row = county_table_unnormalized.query(query).iloc[0]

        if num == 2:
            province = row['PROV_CH']
            prefecture = "NA"
            county = "NA"
        elif num == 4:
            province = row['PROV_CH']
            prefecture = row['CITY_CH']
            county = "NA"
        elif num == 6:
            province = row['PROV_CH']
            prefecture = row['CITY_CH']
            county = row['COUNTY_CH']

        provinces.append(province)
        prefectures.append(prefecture)
        counties.append(county)

    return list(set(provinces)), list(set(prefectures)), list(set(counties))


def match_address(data, county_table, county_table_unnormalized, level_dict):
    data["Match Elements"], data["Match Result"], data["Match Level"], data["Match Error"], data["Match Period"] = zip(*data.apply(lambda x: match_address_row(x, county_table, level_dict), axis=1))
    data["Province"], data["Prefecture"], data["County"] = zip(*data.apply(lambda x: address_structuralize_row(x["Match Result"], county_table_unnormalized), axis=1))
    return data

