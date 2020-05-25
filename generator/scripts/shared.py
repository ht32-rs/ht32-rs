"""
patch.py
Copyright 2020 Henrik Böving

Shared script functions

"""
from sys import version_info

import yaml

from generator import resource

if version_info.minor <= 6:
    # py <=3.6 doesn't include importlib_resources as standard library, use a backport.
    import importlib_resources as resources
else:
    from importlib import resources


def read_device_table():
    """
    Reads the device part table file.
    """
    # since yaml.safe_load is expecting a file stream...
    # inspection always gets this one wrong...
    # noinspection PyTypeChecker
    with resources.open_text(resource, "ht32_part_table.yaml") as ifile:
        return yaml.safe_load(ifile)
