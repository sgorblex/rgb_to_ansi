#!/usr/bin/env python3

import sys
import re
from math import sqrt
import argparse
import json

ansi_rgb = {
    "black": (0, 0, 0),
    "red": (181, 5, 5),
    "green": (15, 181, 15),
    "yellow": (176, 87, 31),
    "blue": (21, 31, 178),
    "magenta": (164, 40, 154),
    "cyan": (79, 184, 204),
    "white": (191, 191, 191),
    "bright_black": (73, 73, 73),
    "bright_red": (255, 94, 90),
    "bright_green": (90, 255, 92),
    "bright_yellow": (232, 255, 82),
    "bright_blue": (66, 101, 216),
    "bright_magenta": (241, 90, 255),
    "bright_cyan": (58, 242, 255),
    "bright_white": (255, 255, 255)
}

ansi_numbers = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "bright_black": "90",
    "bright_red": "91",
    "bright_green": "92",
    "bright_yellow": "93",
    "bright_blue": "94",
    "bright_magenta": "95",
    "bright_cyan": "96",
    "bright_white": "97",
    "reset": "0"
}

ansi_codes = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    "reset": "\033[0m"
}


def closest_ansi_color(r, g, b, palette):
    """Find the ANSI color closest to the given RGB values."""
    closest_color = "black"
    min_distance = float('inf')

    for name, (cr, cg, cb) in palette.items():
        distance = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        if distance < min_distance:
            min_distance = distance
            closest_color = name

    return closest_color

# RESET AFTER EACH CHAR
def convert_rgb_to_ansi(input_string, palette):
    # pattern = re.compile(r'\033\[38;2;(\d+);(\d+);(\d+)m')
    pattern = re.compile(r'\033\[38;2;(\d+);(\d+);(\d+)m(.)')

    def replace_match(match):
        # r, g, b = map(int, match.groups())
        r, g, b = map(int, match.groups()[0:3])
        c = str(match.groups()[3])
        # return ansi_codes[closest_ansi_color(r, g, b)]
        return ansi_codes[closest_ansi_color(r, g, b, palette)] + c + ansi_codes['reset']

    return pattern.sub(replace_match, input_string)

# DO NOT RESET AFTER EACH CHAR
# def convert_rgb_to_ansi(input_string):
#     pattern = re.compile(r'\033\[38;2;(\d+);(\d+);(\d+)m')
#
#     def replace_match(match):
#         r, g, b = map(int, match.groups())
#         # return ansi_codes[closest_ansi_color(r, g, b)]
#         return ansi_codes[closest_ansi_color(r, g, b)]
#
#     return pattern.sub(replace_match, input_string)

def prune_ansi_repetitions(input_string):
    res = input_string

    for color in ansi_codes:
        pattern = r'(\033\['+ansi_numbers[color]+r'm.(\033\[0m)?){2,}'
        doesmatch = re.search(pattern, res)
        if doesmatch:
            def remove_pattern(match):
                singlepattern = r'\033\['+ansi_numbers[color]+r'm(.)(\033\[0m)?'
                def remove_single(matchsingle):
                    return matchsingle.group(1)
                return ansi_codes[color] + re.sub(singlepattern, remove_single, match.group(0)) + ansi_codes['reset']
            res = re.sub(pattern, remove_pattern, res)
    return res

def validate_palette(user_palette, default_palette):
    validated_palette = default_palette.copy()
    for color, value in user_palette.items():
        if color in default_palette and isinstance(value, (list, tuple)) and len(value) == 3 and all(isinstance(v, int) and 0 <= v <= 255 for v in value):
            validated_palette[color] = tuple(value)
        else:
            print(f"'{color}' is not a valid color, ignoring")
    return validated_palette

def load_palette(file_path):
    try:
        with open(file_path, 'r') as file:
            user_palette = json.load(file)
        return validate_palette(user_palette, ansi_rgb)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading palette file: {e}. Falling back to default.")
        return ansi_rgb


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RGB color codes to ANSI escape codes")
    parser.add_argument("--palette", help="Path to custom palette JSON file")
    args = parser.parse_args()

    if args.palette:
        palette = load_palette(args.palette)
    else:
        palette = ansi_rgb


    input_string = sys.stdin.read()  # Read input from standard input
    converted_string = convert_rgb_to_ansi(input_string, palette)
    converted_string = prune_ansi_repetitions(converted_string)
    print(converted_string)
