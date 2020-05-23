#!/usr/bin/env python3
"""
build.py
Copyright 2020 Henrik Böving
"""

import os

print("Cleaning")
os.system("rm -rf svd/*.patched ht32f*")
print("Creating crates")
os.system("./scripts/makecrates.py -y devices")
print("Patching SVD files")
os.system("./scripts/patch.py devices")
print("Generating code")
os.system("./scripts/makemodules.py")
