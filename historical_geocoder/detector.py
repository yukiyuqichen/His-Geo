import json
import os
from .utils.detection import direction_detection_ch as direction_detector_ch

current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)
direction_file_path_ch = os.path.join(current_directory, 'data', 'direction.json')


def detect_direction(data, lang):
    if lang == "ch":
        with open(direction_file_path_ch, "r", encoding="utf-8-sig") as f:
            direction_dictionary = json.load(f)
        directions = direction_dictionary["ch"]["directions"]
        direction_postfixes = direction_dictionary["ch"]["postfixes"]

        direction_with_postfixes = directions.copy()
        for direction in directions:
            for direction_postfix in direction_postfixes:
                direction_with_postfixes.append(direction + direction_postfix)

    direction_detector_ch.detect_direction(data, direction_with_postfixes, direction_postfixes)
    
    return data