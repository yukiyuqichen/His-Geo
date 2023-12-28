import pandas as pd
import re


postfix_list = ["特别行政区", "辖区", "地区", "自治区", "自治县", "自治州", "省", "市", "区", "县", "盟", "委员会"]

minority_list = []
with open("./data/minority_list.txt", "r", encoding="utf-8-sig") as f:
    for line in f.readlines():
        minority_list.append(line.strip())

minority_postfix_list = []
for minority in minority_list:
    if len(minority) > 2:
        minority_postfix_list.append(minority.replace("族", "") + "自治州")
        minority_postfix_list.append(minority.replace("族", "") + "自治区")
        minority_postfix_list.append(minority.replace("族", "") + "自治县")

def normalize_address(str, structure_sign):
    if "自治" in str:
        # Special Cases
        if "内蒙古自治区" in str:
            str = str.replace("内蒙古自治区", "内蒙古")
        if "东乡族自治县" in str:
            str = str.replace("东乡族自治县", "东乡")
        if "龙胜各族自治县" in str:
            str = str.replace("龙胜各族自治县", "龙胜")
        if "河南蒙古族自治县" in str:
            str = str.replace("河南蒙古族自治县", "河南县")
        for postfix in minority_postfix_list:
            if postfix in str:
                str = str.replace(postfix, "")
        for minority in minority_list:
            if minority in str:
                str = str.replace(minority, "")
    if str == "市辖区":
        str == "市辖区"
    else:
        temp_signs = {"河南县":"[temp1]", "河北区":"[temp2]", "津市市":"[temp3]"}
        for temp in temp_signs.keys():
            if temp in str: 
                str = str.replace(temp, temp_signs[temp])
        for postfix in postfix_list:
            if postfix in str and len(str) > 2:
                str = str.replace(postfix, structure_sign)
        for temp in temp_signs.keys():
            if temp_signs[temp] in str:
                str = str.replace(temp_signs[temp], temp)
                
    str = re.sub("（.*）", "", str)
    return str