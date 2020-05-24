"""
patch.py
Copyright 2020 Henrik Böving

Shared script functions

"""
from importlib import resources

import yaml

from generator import resource


def read_device_table():
    """
    Reads the device part table file.
    """
    # since yaml.safe_load is expecting a file stream...
    # inspection always gets this one wrong...
    # noinspection PyTypeChecker
    with resources.open_text(resource, "ht32_part_table.yaml") as ifile:
        return yaml.safe_load(ifile)
