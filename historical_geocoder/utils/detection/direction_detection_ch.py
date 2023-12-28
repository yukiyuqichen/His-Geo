import pandas as pd
import json


with open("./data/direction.json", "r", encoding="utf-8-sig") as f:
    direction_dictionary = json.load(f)

directions = direction_dictionary["ch"]["directions"]
direction_postfixes = direction_dictionary["ch"]["postfixes"]

direction_with_postfixes = directions.copy()
for direction in directions:
    for direction_postfix in direction_postfixes:
        direction_with_postfixes.append(direction + direction_postfix)


def detect_direction_row(row):
    multiple_addresses = row
    # Only deal with single address
    if len(multiple_addresses) == 1:
        address = multiple_addresses[0]
        for direction in direction_with_postfixes:
            if address.endswith(direction):
                for postfix in direction_postfixes:
                    direction_cleaned = direction.replace(postfix, "")
                return [address[:-len(direction)]], direction_cleaned
    return row, None
    

def detect_direction(data):
    data["Address"], data["Direction"] = zip(*data["Address"].apply(lambda x: detect_direction_row(x)))
    return data