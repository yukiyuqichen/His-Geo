import pandas as pd
import re


postfix_list = ["行省", "省", "道", 
                "直隶厅", "厅", 
                "大都督府", "都护府", "都督府", "长史府", "总管府", "直隶府", "羁縻府", "府", 
                "直隶州", "羁縻州", "州", 
                "郡", "县",
                "军民指挥使司",
                "军民宣慰司", "军民安抚司", "蛮夷长官司", "布政使司", 
                "宣慰司", "布政司", "安抚司", "长官司", "宣抚司", "招讨司",
                "巡检司",
                "正司", "副司", "司", 
                "属国都尉", "典农都尉", "屯田都尉", "都尉",
                "委员", "理事官", 
                ]


def normalize_address(str, structure_sign):
    if pd.notnull(str):
        temp_signs = {}
        for temp in temp_signs.keys():
            if temp in str: 
                str = str.replace(temp, temp_signs[temp])

        for postfix in postfix_list:
            # if postfix is the last word in str
            if str.endswith(postfix):
                str_normalized = str.replace(postfix, structure_sign)
                if len(str_normalized) > 1 + len(structure_sign):
                    str = str_normalized

        for temp in temp_signs.keys():
            if temp_signs[temp] in str:
                str = str.replace(temp_signs[temp], temp)
        str = re.sub("（.*）", "", str)
        return str
    else:
        return str