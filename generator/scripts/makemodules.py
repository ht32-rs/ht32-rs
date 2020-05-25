#!/usr/bin/env python3
"""
makemodules.py
Copyright 2020 Henrik Böving
Licensed under the MIT and Apache 2.0 licenses.

Usage: python3 scripts/makemodules.py devices/
"""
import pathlib
import subprocess

from loguru import logger

from .shared import read_device_table

ROOT = pathlib.Path().absolute()
SVD_DIR = ROOT / "svd"
RUST_FMT = ROOT / "rustfmt.toml"


def make_modules():
    table = read_device_table()

    for crate in table:

        for module in table[crate]:
            output_patch = SVD_DIR / f"{module}.svd.patched"
            logger.info("Generating code for {}", output_patch.absolute())
            module_dir = ROOT / crate / "src" / module
            module_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("entering {}", module_dir.absolute())
            svd_result = subprocess.check_call(
                ["svd2rust", "-g", "-i", f"{output_patch.absolute()}"], cwd=module_dir
            )
            logger.debug("check_call svd2rust := {}", svd_result)
            (module_dir / "build.rs").unlink()
            (module_dir / "generic.rs").replace(module_dir / ".." / "generic.rs")
            (module_dir / "lib.rs").replace(module_dir / "mod.rs")
            form_result = subprocess.check_call(["form", "-i", "mod.rs", "-o", "."], cwd=module_dir)
            logger.debug("check_call form := {}", form_result)
            (module_dir / "lib.rs").replace(module_dir / "mod.rs")
            rustfmt_args = ["rustfmt", f"--config-path={RUST_FMT.absolute()}"]
            rustfmt_args.extend(module_dir.glob("*.rs"))
            rustfmt_result = subprocess.check_call(rustfmt_args, cwd=module_dir)
            logger.debug("check_call rustfmt := {}", rustfmt_result)
            lines = (module_dir / "mod.rs").read_text().splitlines(keepends=True)

            # these are lines that annoy rustc
            banned = [
                "#![deny(legacy_directory_ownership)]",
                "#![deny(plugin_as_library)]",
                "#![deny(safe_extern_statics)]",
                "#![deny(unions_with_drop_fields)]",
                "#![no_std]",
            ]
            to_remove = [i for i, line in enumerate(lines) if line.strip() in banned]
            for i in reversed(to_remove):
                del lines[i]
            with (module_dir / "mod.rs").open("w") as ofile:
                ofile.writelines(lines)


if __name__ == "__main__":
    make_modules()
