#!/usr/bin/env python

import os
import re
import yaml
import pathlib

# FUNCTIONS


# TODO: Add Logging


# File processing utilities
def read_yaml(
    file_name: str,
    folder_path: str = str(),
) -> dict:
    """Used to get data from inside a YAML file"""
    if not folder_path:
        folder_path = pathlib.Path(__file__).parent.resolve()

    yaml_data = {}
    yaml_path = os.path.join(
        folder_path,
        file_name,
    )
    with open(yaml_path) as config_file:
        try:
            yaml_data = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc)

    return yaml_data


# List processing utilities
def get_byid_stripped(
    input_list: list,
    entry_id: int,
    def_str: str = str(),
) -> str:
    """Safely return a string from a list using its id"""

    if len(input_list) > entry_id:
        return input_list[entry_id].strip()

    else:
        return def_str


def get_byid_split(
    input_string: str,
    string_separator: str,
    default_value: str,
    items_count: int,
) -> list:
    """Get multiple items from an input string"""

    # Initialize lists
    split_values = tuple()
    split_items = input_string.split(string_separator)

    # Iterate over all split items
    for item_id in range(0, items_count):

        item_value = get_byid_stripped(
            input_list=split_items,
            entry_id=item_id,
            def_str=default_value,
        )
        split_values += (item_value,)

    return split_values


# Simple objects (str, int, float) processing utilities
def get_snake_case(
    input_string: str,
) -> str:
    """Convert input string to a snake case formatted string"""

    clean_string = input_string

    substitutions = [
        {
            "old": "\-",
            "new": " ",
        },
        {
            "old": "([A-Z]+)",
            "new": r" \1",
        },
        {
            "old": "([A-Z][a-z]+)",
            "new": r" \1",
        },
        {
            "old": "\.",
            "new": r"_",
        },
    ]

    for sub_couple in substitutions:
        clean_string = re.sub(
            sub_couple["old"],
            sub_couple["new"],
            clean_string,
        )

    return "_".join(clean_string.split()).lower()


def clean_float(
    input_value: float,
    replacement_value: float,
    precision: int,
) -> float:
    """Clean integer and replace it if required"""
    try:
        cleaned_value = round(float(input_value), precision)
    except:
        cleaned_value = replacement_value
    return cleaned_value
