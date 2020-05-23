#!/usr/bin/env python3
"""
build.py
Copyright 2020 Henrik Böving
"""
from loguru import logger
import pathlib
import os

CWD = pathlib.Path()
SVD = CWD / "svd"

logger.info("Cleaning")
for patch in SVD.glob("*.patched"):
    logger.debug("deleting {}", patch.absolute())
    patch.unlink()
# idk how to do this in pathlib
os.system("rm -rf ht32f*")
logger.info("Creating crates")

os.system("./scripts/makecrates.py -y devices")
logger.info("Patching SVD files")
os.system("./scripts/patch.py devices")
logger.info("Generating code")
os.system("./scripts/makemodules.py")
