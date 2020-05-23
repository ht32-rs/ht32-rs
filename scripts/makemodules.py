#!/usr/bin/env python3
"""
makemodules.py
Copyright 2020 Henrik Böving
Licensed under the MIT and Apache 2.0 licenses.

Usage: python3 scripts/makemodules.py devices/
"""
import os
import yaml

def main():
    path = os.path.join(
        os.path.abspath(os.path.split(__file__)[0]), os.pardir,
        "ht32_part_table.yaml")

    with open(path, encoding='utf-8') as f:
        table = yaml.safe_load(f)

    for crate in table:

        for module in table[crate]:
            print(f"Generating code for svd/{module}.svd.patched")
            os.chdir(crate)
            os.mkdir(f"src/{module}")
            os.chdir(f"src/{module}")
            os.system(f"svd2rust -g  -i ../../../svd/{module}.svd.patched")
            os.remove("build.rs")
            os.rename("generic.rs", "../generic.rs")
            os.rename("lib.rs", "mod.rs")
            os.system("form -i mod.rs -o .")
            os.rename("lib.rs", "mod.rs")
            os.system("rustfmt --config-path=../../../rustfmt.toml ./*.rs")
            mod = open("mod.rs", "r")
            lines = mod.readlines()
            mod.close()

            # these are lines that annoy rustc
            banned = [
                "#![deny(legacy_directory_ownership)]",
                "#![deny(plugin_as_library)]",
                "#![deny(safe_extern_statics)]",
                "#![deny(unions_with_drop_fields)]",
                "#![no_std]"
            ]

            mod = open("mod.rs", "w")
            for line in lines:
                if line.strip() not in banned:
                    mod.write(line)
            mod.close()
            os.chdir("../../../")

if __name__ == "__main__":
    main()
