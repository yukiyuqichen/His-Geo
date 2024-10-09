import pandas as pd
import requests
import itertools
import time
import re
from retrying import retry
from shapely.geometry import Point

import opencc
converter = opencc.OpenCC('t2s.json')


def generate_n_grams_chinese(text):
    """ Generate n-grams from a given Chinese text for all n from 2 to the length of text. """
    max_n = len(text)
    n_grams = []
    for n in range(2, max_n + 1):
        for i in range(len(text) - n + 1):
            n_gram = text[i:i + n]
            n_grams.append(n_gram)
    
    return n_grams


def print_retry_details(exception):
    print(f"Error happened: {exception}")
    print("Retrying...")
    return True


@retry(retry_on_exception=print_retry_details)
def invoke_api(toponym):
    # wait for some time to avoid exceeding the limit of the API
    time.sleep(3)
    toponym = converter.convert(toponym)
    url = f"https://maps.cga.harvard.edu/tgaz/placename?fmt=json&n={toponym}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["placenames"]
    else:
        return None


def search_gazetteer(toponym, gazetteer):
    toponym = converter.convert(toponym)
    df_response = gazetteer[gazetteer['NAME_SIM']==toponym].copy()
    if len(df_response) == 0:
        return None
    else:
        responses = []
        for index, row in df_response.iterrows():
            response = {"sys_id": row["TGAZ_ID"],
                        "name": row["NAME_SIM"],
                        "begin": row["BEG"],
                        "end": row["END"],
                        "parent sys_id": row["PARTOF_ID"],
                        "parent name": row["PARTOF_SIM"],
                        "feature type": row["TYPE_SIM"],
                        "xy coordinates": str(row["X"]) + ", " + str(row["Y"]),
                        "X": row["X"],
                        "Y": row["Y"]}
            responses.append(response)
        return responses


def match_address_row_offline(row, county_table, gazetteer, level_dict):
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
    geometry = None

    toponyms = gazetteer["NAME_SIM"].tolist()

    for address in addresses:
        for county_name in toponyms:
            match_results_id = {}
            match_results_element = []
            address_temp = address
            if county_name in address_temp:
                match_results_element.append(county_name)
                address_temp = address_temp.replace(county_name, "")

                prefectures = search_gazetteer(county_name, gazetteer)
                if len(prefectures) > 0:
                    match_period = "historic"
                    for j in range(len(prefectures)):
                        match_results_id["county"] = prefectures[j]["sys_id"]
                        new_row = {"id": match_results_id,
                                   "element": match_results_element,
                                   "match_num": len(match_results_id)}
                        match_dataframe.loc[len(match_dataframe)] = new_row

                        prefecture = prefectures[j]["parent name"].split(" ")[0]
                        if prefecture != "" and prefecture in address_temp:
                            match_results_element_pref = match_results_element.copy()
                            match_results_id_pref = match_results_id.copy()
                            match_results_element_pref.append(prefecture)
                            match_results_id_pref["prefecture"] = prefectures[j]["parent sys_id"]

                            new_row = {"id": match_results_id_pref,
                                    "element": match_results_element_pref,
                                    "match_num": len(match_results_id_pref)}
                            match_dataframe.loc[len(match_dataframe)] = new_row

                            address_temp = address_temp.replace(prefecture, "")
                            # In early periods, there are often no provinces but dynasties in this field
                            provinces = invoke_api(prefecture)
                            for k in range(len(provinces)):
                                province = provinces[k]["parent name"].split(" ")[0]
                                if province != "" and province in address_temp:
                                    match_results_element_prov = match_results_element_pref.copy()
                                    match_results_id_prov = match_results_id_pref.copy()
                                    match_results_element_prov.append(province)
                                    match_results_id_prov["province"] = provinces[k]["parent sys_id"]

                                    new_row = {"id": match_results_id_prov,
                                               "element": match_results_element_prov,
                                               "match_num": len(match_results_id_prov)}
                                    match_dataframe.loc[len(match_dataframe)] = new_row

        match_dataframe = match_dataframe.drop_duplicates(subset=["element"]).reset_index(drop=True)
        print(match_dataframe)

        if len(match_dataframe) == 0:
            match_level = 0
            match_errors.append("No Match")

        elif len(match_dataframe) == 1:
            match = match_dataframe.iloc[0]
            match_elements.append(match["element"])
            if "county" in match["id"].keys():
                match_final.append({"county": match["id"]["county"]})
                match_level = 3
                for result in prefectures:
                    if result["sys_id"] == match["id"]["county"]:
                        geometry = result["xy coordinates"].split(", ")
                        break
                print("Geometry: ", geometry)
                if geometry != None:
                    geometry = (float(geometry[0]), float(geometry[1]))
                    geometry = Point(geometry)
            elif "prefecture" in match["id"].keys():
                match_final.append({"prefecture": match["id"]["prefecture"]})
                match_level = 2
            elif "province" in match["id"].keys():
                match_final.append({"province": match["id"]["province"]})
                match_level = 1

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
                geometry = None
                print(prefectures)
                print(match)
                if "county" in match["id"].keys():
                    match_final.append({"county": match["id"]["county"]})
                    match_level = 3
                    for result in prefectures:
                        if result["sys_id"] == match["id"]["county"]:
                            geometry = result["xy coordinates"].split(", ")
                            print(geometry)
                            break
                    if geometry != None:
                        geometry = (float(geometry[0]), float(geometry[1]))
                        geometry = Point(geometry)
                elif "prefecture" in match["id"].keys():
                    match_final.append({"prefecture": match["id"]["prefecture"]})
                    match_level = 2
                elif "province" in match["id"].keys():
                    match_final.append({"province": match["id"]["province"]})
                    match_level = 1
                
    match_level = level_dict[match_level]

    print(match_elements, match_final, match_level, match_errors, match_period, geometry)

    if row["Match Result"] is not None:
        match_elements_previous, match_final_previous, match_level_previous, match_errors_previous, match_period_previous, geometry_previous = row["Match Elements"], row["Match Result"], row["Match Level"], row["Match Error"], row["Match Period"], row["geometry"]
        if len(match_elements) == 0:
            return match_elements_previous, match_final_previous, match_level_previous, match_errors_previous, match_period_previous, geometry_previous
        else:
            elements_length_previous = len("".join(match_elements_previous[0]))
            elements_length_current = len("".join(match_elements[0]))
            if elements_length_current > elements_length_previous:
                return match_elements, match_final, match_level, match_errors, match_period, geometry
            else:
                return match_elements_previous, match_final_previous, match_level_previous, match_errors_previous, match_period_previous, geometry_previous
    else:
        return match_elements, match_final, match_level, match_errors, match_period, geometry

def match_address_row_online(row, county_table, level_dict):
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
    geometry = None

    counties_set = set(county_table["NAME_CH"].tolist())

    for address in addresses:
        for county_name in counties_set:
            match_results_id = {}
            match_results_element = []
            address_temp = address
            if county_name in address_temp:
                match_results_element.append(county_name)
                address_temp = address_temp.replace(county_name, "")

                prefectures = invoke_api(county_name)
                if len(prefectures) > 0:
                    match_period = "historic"
                    for j in range(len(prefectures)):
                        match_results_id["county"] = prefectures[j]["sys_id"]
                        new_row = {"id": match_results_id,
                                   "element": match_results_element,
                                   "match_num": len(match_results_id)}
                        match_dataframe.loc[len(match_dataframe)] = new_row

                        prefecture = prefectures[j]["parent name"].split(" ")[0]
                        if prefecture != "" and prefecture in address_temp:
                            match_results_element_pref = match_results_element.copy()
                            match_results_id_pref = match_results_id.copy()
                            match_results_element_pref.append(prefecture)
                            match_results_id_pref["prefecture"] = prefectures[j]["parent sys_id"]

                            new_row = {"id": match_results_id_pref,
                                    "element": match_results_element_pref,
                                    "match_num": len(match_results_id_pref)}
                            match_dataframe.loc[len(match_dataframe)] = new_row

                            address_temp = address_temp.replace(prefecture, "")
                            # In early periods, there are often no provinces but dynasties in this field
                            provinces = invoke_api(prefecture)
                            for k in range(len(provinces)):
                                province = provinces[k]["parent name"].split(" ")[0]
                                if province != "" and province in address_temp:
                                    match_results_element_prov = match_results_element_pref.copy()
                                    match_results_id_prov = match_results_id_pref.copy()
                                    match_results_element_prov.append(province)
                                    match_results_id_prov["province"] = provinces[k]["parent sys_id"]

                                    new_row = {"id": match_results_id_prov,
                                               "element": match_results_element_prov,
                                               "match_num": len(match_results_id_prov)}
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
                for result in prefectures:
                    if result["sys_id"] == match["id"]["county"]:
                        geometry = result["xy coordinates"].split(", ")
                        break
                if geometry != None:
                    geometry = (float(geometry[0]), float(geometry[1]))
                    geometry = Point(geometry)
            elif "prefecture" in match["id"].keys():
                match_final.append({"prefecture": match["id"]["prefecture"]})
                match_level = 2
            elif "province" in match["id"].keys():
                match_final.append({"province": match["id"]["province"]})
                match_level = 1

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
                    for result in prefectures:
                        if result["sys_id"] == match["id"]["county"]:
                            geometry = result["xy coordinates"].split(", ")
                            break
                    if geometry != None:
                        geometry = (float(geometry[0]), float(geometry[1]))
                        geometry = Point(geometry)
                elif "prefecture" in match["id"].keys():
                    match_final.append({"prefecture": match["id"]["prefecture"]})
                    match_level = 2
                elif "province" in match["id"].keys():
                    match_final.append({"province": match["id"]["province"]})
                    match_level = 1
                
    match_level = level_dict[match_level]

    print(match_elements, match_final, match_level, match_errors, match_period, geometry)

    if row["Match Result"] is not None:
        match_elements_previous, match_final_previous, match_level_previous, match_errors_previous, match_period_previous, geometry_previous = row["Match Elements"], row["Match Result"], row["Match Level"], row["Match Error"], row["Match Period"], row["geometry"]
        if len(match_elements) == 0:
            return match_elements_previous, match_final_previous, match_level_previous, match_errors_previous, match_period_previous, geometry_previous
        else:
            elements_length_previous = len("".join(match_elements_previous[0]))
            elements_length_current = len("".join(match_elements[0]))
            if elements_length_current > elements_length_previous:
                return match_elements, match_final, match_level, match_errors, match_period, geometry
            else:
                return match_elements_previous, match_final_previous, match_level_previous, match_errors_previous, match_period_previous, geometry_previous
    else:
        return match_elements, match_final, match_level, match_errors, match_period, geometry
    

def address_structuralize_row(match_elements, county_table):

    provinces = []
    prefectures = []
    counties = []

    for element in match_elements:
        try:
            counties.append(element[0])
        except:
            pass
        try:
            prefectures.append(element[1])
        except:
            pass
        try:
            provinces.append(element[2])
        except:
            pass

    return list(set(provinces)), list(set(prefectures)), list(set(counties))


def filter_his_address(row):
    pattern = "道|路|州|府|郡"
    addresses = row["Address"]
    for address in addresses:
        if re.search(pattern, address):
            return True
    return False


def match_address(data, county_table, gazetteer, level_dict, year_range):
    # Filter historic addresses
    # data["id"] = data.index
    # data_remaining = data[data.apply(lambda x: not filter_his_address(x), axis=1)].copy()
    # data_filtered = data[data.apply(lambda x: filter_his_address(x), axis=1)].copy()
    # data_filtered["Match Elements"], data_filtered["Match Result"], data_filtered["Match Level"], data_filtered["Match Error"], data_filtered["Match Period"], data_filtered["geometry"] = zip(*data_filtered.apply(lambda x: match_address_row_offline(x, county_table, gazetteer, level_dict), axis=1))
    # data_filtered["Province"], data_filtered["Prefecture"], data_filtered["County"] = zip(*data_filtered.apply(lambda x: address_structuralize_row(x["Match Elements"], county_table), axis=1))
    # data = pd.concat([data_remaining, data_filtered]).set_index("id").sort_index()

    data["Match Elements"], data["Match Result"], data["Match Level"], data["Match Error"], data["Match Period"], data["geometry"] = zip(*data.apply(lambda x: match_address_row_offline(x, county_table, gazetteer, level_dict), axis=1))
    data["Province"], data["Prefecture"], data["County"] = zip(*data.apply(lambda x: address_structuralize_row(x["Match Elements"], county_table), axis=1))

    return data

