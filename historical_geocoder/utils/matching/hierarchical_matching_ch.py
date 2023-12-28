import pandas as pd


def match_address_row(row, county_table, level_dict):
    """
    Input: 
           row is a row of the dataframe
           row["Address"] is a list of multiple addresses 
           most times it only inclues one address
    Return: 
            match_level is a str (None, "Province", "City", "County")
            match_final is a list of the most accurate codes
            match_errors is a list of errors
    """
    multiple_addresses = row["Address"]
    match_dict = {}
    match_final = []
    match_errors = []
    for address in multiple_addresses:
        for i in range(len(county_table)):
            match_results = {}
            address_temp = address
            province_name = county_table.loc[i, "PROV_CH"]
            if province_name in address_temp:
                match_results["province"] = county_table.loc[i, "PCODE"]
                address_temp = address_temp.replace(province_name, "")
            
            city_name = county_table.loc[i, "CITY_CH"]
            if city_name in address_temp:
                match_results["city"] = county_table.loc[i, "DCODE"]
                address_temp = address_temp.replace(city_name, "")

            county_name = county_table.loc[i, "COUNTY_CH"]
            if county_name in address_temp:
                match_results["county"] = county_table.loc[i, "CODE2020"]
                address_temp = address_temp.replace(county_name, "")
                
            if len(match_results) > 0:
                if len(match_results) not in match_dict.keys():
                    match_dict[len(match_results)] = []
                if match_results not in match_dict[len(match_results)]:
                    match_dict[len(match_results)].append(match_results)

    if len(match_dict.keys()) == 0:
        match_level = 0
        match_errors.append("No Match")

    else:
        maxium = max(list(match_dict.keys()))
        match_max = match_dict[maxium]
        for match in match_max:
            if "county" in match.keys():
                match_final.append({"county": match["county"]})
                match_level = 3
            elif "city" in match.keys():
                match_final.append({"city": match["city"]})
                match_level = 2
            elif "province" in match.keys():
                match_final.append({"province": match["province"]})
                match_level = 1
                
        match_level = level_dict[match_level]

        if len(match_final) > 1:
            match_errors.append("Multiple Matches")

    return match_final, match_level, match_errors


def address_structuralize_row(match_results, county_table):

    codes = [list(i.values())[0] for i in match_results]

    provinces = []
    cities = []
    counties = []

    for code in codes:

        num = len(str(code))

        if num == 2:
            query = f"PCODE == {code}"
        elif num == 4:
            query = f"DCODE == {code}"
        elif num == 6:
            query = f"CODE2020 == {code}"

        row = county_table.query(query).iloc[0]

        province = row['PROV_CH'] if 'PROV_CH' in row else "NA"
        city = row['CITY_CH'] if 'CITY_CH' in row else "NA"
        county = row['COUNTY_CH'] if 'COUNTY_CH' in row else "NA"

        provinces.append(province)
        cities.append(city)
        counties.append(county)

    return list(set(provinces)), list(set(cities)), list(set(counties))


def match_address(data, county_table, level_dict):
    data["Match Result"], data["Match Level"], data["Match Error"] = zip(*data.apply(lambda x: match_address_row(x, county_table, level_dict), axis=1))
    data["Province"], data["City"], data["County"] = zip(*data.apply(lambda x: address_structuralize_row(x["Match Result"], county_table), axis=1))
    return data

