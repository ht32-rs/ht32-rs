#!/usr/bin/env python3
"""
patch.py
Copyright 2020 Henrik Böving

Patch all the SVDs mentioned in a certain directory

Usage: python3 scripts/patch.py devices/
"""

from os import listdir
from os.path import isfile, join
import argparse
import os
import svdtools

def main(device_path):
    device_files = [f for f in listdir(device_path) if isfile(join(device_path, f))]
    [svdtools.patch.main(f"{device_path}/{f}") for f in device_files]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("devices", help="Path to device YAML files")
    args = parser.parse_args()
    main(args.devices)
