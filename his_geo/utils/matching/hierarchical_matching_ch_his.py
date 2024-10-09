import pandas as pd
import itertools
from pandarallel import pandarallel


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

def match_address_row(row, gazetteer_filtered, level_dict, year_range):
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
    match_dataframe = pd.DataFrame(columns=["id", "element", "match_num", "match_level"])
    match_elements = []
    match_final = []
    match_errors = []
    match_levels = []
    match_period = None



    print(addresses)
    
    for address in addresses:
        for i in range(len(gazetteer_filtered)):
            match_results_id = {}
            match_results_element = []
            address_temp = address
            match_level = None

            for j in range(1, len(level_dict)):
                lev_name = gazetteer_filtered.loc[i, f"LEV{j}_NAME"]
                if pd.notnull(lev_name):
                    if lev_name in address_temp:
                        if match_level is None:
                            match_level = gazetteer_filtered.loc[i, f"LEV{j}_TYPE"]
                        match_results_element.append(lev_name)
                        match_results_id[f"LEV{j}"] = gazetteer_filtered.loc[i, f"LEV{j}_ID"]
                        address_temp = address_temp.replace(lev_name, "")

            if len(match_results_id) > 0:
                new_row = {"id": match_results_id,
                           "element": match_results_element,
                           "match_num": len(match_results_id),
                           "match_level": match_level}
                match_dataframe.loc[len(match_dataframe)] = new_row

        match_dataframe = match_dataframe.drop_duplicates(subset=["element"]).reset_index(drop=True)

        if len(match_dataframe) == 0:
            match_level = 0
            match_errors.append("No Match")

        elif len(match_dataframe) == 1:
            match = match_dataframe.iloc[0]
            match_elements.append(match["element"])
            match_levels.append(match["match_level"])
            
            for i in range(1, len(level_dict)):
                if f"LEV{i}" in match["id"].keys():
                    match_final.append({f"LEV{i}": match["id"][f"LEV{i}"]})
                    break

            match_period = "historic"

        else:
            match_num_max = match_dataframe["match_num"].max()
            match_max = match_dataframe[match_dataframe["match_num"] == match_num_max]
            if len(match_max) > 1:
                match_max["element_length"] = match_max["element"].apply(lambda x: len("".join(list(itertools.chain(*x)))))
                match_max = match_max[match_max["element_length"] == match_max["element_length"].max()]
                if len(match_max) > 1:
                    match_errors.append("Multiple Matches")

            for id, match in match_max.iterrows():
                match_elements.append(match["element"])    
                match_levels.append(match["match_level"])
                for i in range(1, len(level_dict)):
                    if f"LEV{i}" in match["id"].keys():
                        match_final.append({f"LEV{i}": match["id"][f"LEV{i}"]})
                        break

            match_period = "historic"

    print(match_elements, match_final, match_levels, match_errors, match_period)

    # if row["Match Result"] is not None:
    if len(row["Match Result"]) > 0:
        match_elements_previous, match_final_previous, match_levels_previous, match_errors_previous, match_period_previous = row["Match Elements"], row["Match Result"], row["Match Level"], row["Match Error"], row["Match Period"]
        if len(match_elements) == 0:
            return match_elements_previous, match_final_previous, match_levels_previous, match_errors_previous, match_period_previous
        else:
            elements_length_previous = len("".join(match_elements_previous[0]))
            elements_length_current = len("".join(match_elements[0]))
            if elements_length_current > elements_length_previous:
                return match_elements, match_final, match_levels, match_errors, match_period
            else:
                return match_elements_previous, match_final_previous, match_levels_previous, match_errors_previous, match_period_previous
    else:
        return match_elements, match_final, match_levels, match_errors, match_period



def address_structuralize_row(match_results, gazetteer_unnormalized, level_dict):

    codes = [list(i.values())[0] for i in match_results]

    result_dict = {}
    for i in range(1, len(level_dict)):
        result_dict[f"LEV{i}"] = []
    
    begins = []
    ends = []

    for code in codes:
    
        for i in range(1, len(level_dict)):
            query = f"LEV{i}_ID == '{code}'"
            query_result = gazetteer_unnormalized.query(query)
            if len(query_result) > 0:
                row = gazetteer_unnormalized.query(query).iloc[0]
                begins.append(row[f"LEV{i}_BEG"])
                ends.append(row[f"LEV{i}_END"])
                for j in range(i, len(level_dict)):
                    if pd.notnull(row[f"LEV{j}_NAME"]):
                        result_dict[f"LEV{j}"].append(row[f"LEV{j}_NAME"])
                break

    return result_dict["LEV1"], result_dict["LEV2"], result_dict["LEV3"], result_dict["LEV4"], result_dict["LEV5"], begins, ends


def match_address(data, gazetteer, gazetteer_unnormalized, level_dict, year_range):
    if year_range != ():
        gazetteer_filtered = gazetteer[(gazetteer["BEG"] <= year_range[1]) & (gazetteer["END"] >= year_range[0])].reset_index(drop=True)
        gazetteer_unnormalized_filtered = gazetteer_unnormalized[(gazetteer_unnormalized["BEG"] <= year_range[1]) & (gazetteer_unnormalized["END"] >= year_range[0])].reset_index(drop=True)
    else:
        gazetteer_filtered = gazetteer
        gazetteer_unnormalized_filtered = gazetteer_unnormalized

    pandarallel.initialize(progress_bar=True)
    data["Match Elements"], data["Match Result"], data["Match Level"], data["Match Error"], data["Match Period"] = zip(*data.parallel_apply(lambda x: match_address_row(x, gazetteer_filtered, level_dict, year_range), axis=1))
    data["LEV1"], data["LEV2"], data["LEV3"], data["LEV4"], data["LEV5"], data['BEG'], data['END'] = zip(*data.parallel_apply(lambda x: address_structuralize_row(x["Match Result"], gazetteer_unnormalized_filtered, level_dict), axis=1))
    return data

