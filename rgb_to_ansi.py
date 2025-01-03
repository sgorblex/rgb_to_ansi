#!/usr/bin/env python3

import sys
import re
from math import sqrt
import argparse
import json

# default palette
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
def convert_rgb_to_ansi(input_string, palette, reset):
    if reset:
        pattern = re.compile(r'\033\[38;2;(\d+);(\d+);(\d+)m(.)')

        def replace_match(match):
            groups = match.groups()
            r, g, b = map(int, groups[:3])
            c = groups[3]
            return '\033['+ansi_numbers[closest_ansi_color(r, g, b, palette)]+'m' + c + '\033[0m'

        return pattern.sub(replace_match, input_string)

    else:
        pattern = re.compile(r'\033\[38;2;(\d+);(\d+);(\d+)m')

        def replace_match(match):
            r, g, b = map(int, match.groups())
            return '\033['+ansi_numbers[closest_ansi_color(r, g, b, palette)]+'m'

        return pattern.sub(replace_match, input_string)


# TODO: could be improved to work on mnulticharacter colored sequences
def prune_ansi_repetitions(input_string):
    res = input_string

    for colornumber in ansi_numbers.values():
        pattern = r'(\033\['+colornumber+r'm.(\033\[0m)?){2,}'
        doesmatch = re.search(pattern, res)
        if doesmatch:
            def remove_pattern(match):
                singlepattern = r'\033\['+colornumber+r'm(.)(\033\[0m)?'
                def remove_single(matchsingle):
                    return matchsingle.group(1)
                return '\033['+colornumber+'m' + re.sub(singlepattern, remove_single, match.group(0)) + '\033[0m'
        
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
    parser.add_argument('--no-pruning', action='store_true', help='Disable pruning of repeated ANSI codes, which compresses the output when it has consecutive same-colored pixels. Needed if the input is not a single character per color code.')
    parser.add_argument('--no-reset', action='store_true', help='Does not reset color after each character. Might bring to wrong colors in the output.')

    args = parser.parse_args()

    if args.palette:
        palette = load_palette(args.palette)
    else:
        palette = ansi_rgb


    input_string = sys.stdin.read()
    converted_string = convert_rgb_to_ansi(input_string, palette , not args.no_reset)
    if not args.no_pruning:
        converted_string = prune_ansi_repetitions(converted_string)
    print(converted_string)
