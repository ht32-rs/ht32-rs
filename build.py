#!/usr/bin/env python3
"""
build.py
Copyright 2020 Henrik Böving
"""
import sys

from loguru import logger
import pathlib
import os
from generator.scripts import makemodules, patch, makecrates
import subprocess
# logger setup
logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<k>[</>{time} <level>{level}</> <green>{module}.{function}:{line}</><k>]</> "
                  "<level>{message}</>", level="INFO")

# grab absolute path to the CWD, just in case something fiddles with the CWD...
CWD = pathlib.Path().absolute()
SVD = CWD / "svd"
DEVICES = CWD / "devices"

logger.info("Cleaning")
for patched in SVD.glob("*.patched"):
    logger.debug("deleting {}", patched.absolute())
    patched.unlink()
# idk how to do this in pathlib without making a giant mess...
subprocess.check_call(["rm", "-rf", "ht32f*"])
logger.info("Creating crates")
makecrates.make_crates(DEVICES, True)
logger.info("Patching SVD files")
patch.patch_files(DEVICES)
logger.info("Generating code")
makemodules.make_modules()
