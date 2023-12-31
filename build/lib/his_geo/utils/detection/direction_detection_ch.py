import pandas as pd
import json


def detect_direction_row(row, direction_with_postfixes, direction_postfixes):
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
    

def detect_direction(data, direction_with_postfixes, direction_postfixes):
    data["Address"], data["Direction"] = zip(*data["Address"].apply(lambda x: detect_direction_row(x, direction_with_postfixes, direction_postfixes)))
    return data