#!/usr/bin/env python3

"""
makecrates.py
Copyright 2017-2019 Adam Greig
Copyright 2020 Henrik Böving
Licensed under the MIT and Apache 2.0 licenses.

Autogenerate the crate Cargo.toml, build.rs, README.md and src/lib.rs files
based on available YAML files for each HT32 family.

Usage: python3 scripts/makecrates.py devices/
"""
import argparse
import glob
import os
import os.path
from importlib import resources
from pathlib import Path
from typing import Dict, List
import yaml
from loguru import logger

from generator import resource

VERSION = "0.1.0"
SVD2RUST_VERSION = "0.17.0"

CRATE_DOC_FEATURES = {
    "ht32f0yyy": ["rt", "ht32f0006", "ht32f0008"],
    "ht32f1xxxx": ["rt", "ht32f12345", "ht32f12364", "ht32f12365_66"],
    "ht32f1yyy": ["rt", "ht32f125x", "ht32f1653_54", "htf32f1655_56", "ht32f175x"],
    "ht32f2xxxx": ["rt", "ht32f22366"],
    "ht32f2yyy": ["rt", "ht32f275x"],
    "ht32f5xxxx": [
        "rt",
        "ht32f50220_30",
        "ht32f50231_41",
        "ht32f50343",
        "ht32f52142",
        "ht32f52220_30",
        "ht32f52231_41",
        "ht32f52243_53",
        "ht32f52331_41",
        "ht32f52342_52",
        "þ32f52344_54",
        "ht32f52357_67",
        "ht32f57331_41",
        "ht32f57342_52",
        "ht32f59041",
        " ht32f59741",
    ],
    "ht32f5yyy": ["rt", "ht32f5826"],
    "ht32f6xxxx": ["rt", "ht32f61352", "ht32f65230_40"],
}
CWD = Path()
# inspection always gets this one wrong...
# noinspection PyTypeChecker
CARGO_TOML_TPL = resources.read_text(resource, "cargo.toml.template")

# inspection always gets this one wrong...
# noinspection PyTypeChecker
SRC_LIB_RS_TPL = resources.read_text(resource, "src_lib.rs.template")

# inspection always gets this one wrong...
# noinspection PyTypeChecker
README_TPL = resources.read_text(resource, "README.template")

# inspection always gets this one wrong...
# noinspection PyTypeChecker
BUILD_TPL = resources.read_text(resource, "build.rs.template")


def read_device_table():
    # since yaml.safe_load is expecting a file stream...
    # inspection always gets this one wrong...
    # noinspection PyTypeChecker
    with resources.open_text(resource, "ht32_part_table.yaml") as ifile:
        return yaml.safe_load(ifile)


def make_device_rows(table, family):
    rows = []
    for device, dt in table[family].items():
        links = "[{}]({}), [st.com]({})".format(dt["um"], dt["um_url"], dt["url"])
        members = ", ".join(m for m in dt["members"])
        rows.append("| {} | {} | {} |".format(device, members, links))
    return "\n".join(sorted(rows))


def make_features(devices):
    return "\n".join("{} = []".format(d) for d in sorted(devices))


def make_mods(devices):
    return "\n".join('#[cfg(feature = "{0}")]\npub mod {0};\n'.format(d) for d in sorted(devices))


def make_device_clauses(devices):
    return (
        " else ".join(
            """\
        if env::var_os("CARGO_FEATURE_{}").is_some() {{
            "src/{}/device.x"
        }}""".strip().format(
                d.upper(), d
            )
            for d in sorted(devices)
        )
        + ' else { panic!("No device features selected"); }'
    )


def make_crates(devices_path: Path, yes: bool):
    devices: Dict[str, List[str]] = {}

    for path in devices_path.glob("*.yaml"):
        yamlfile = path.stem
        family_string = yamlfile.split("_")[0]
        family = family_string[:6]
        logger.debug("family_string := {!r}", family_string)
        if len(family_string) == 10:
            family = f"{family}xxxx"
        elif len(family_string) == 9:
            family = f"{family}yyy"
        else:
            print(f"The yaml file name '{yamlfile}' does not fit the format we expect")
            exit(1)
        device = path.stem.lower()
        if family not in devices:
            devices[family] = []
        logger.debug("new device {!r}", device)
        devices[family].append(device)

    table = read_device_table()

    dirs = [CWD / family for family in devices]
    logger.info("Going to create/update the following directories: {}", dirs)
    if not yes:
        input("Enter to continue, ctrl-C to cancel")

    for family in devices:
        devices[family] = sorted(devices[family])
        crate = family.lower()
        features = make_features(devices[family])
        clauses = make_device_clauses(devices[family])
        mods = make_mods(devices[family])
        ufamily = family.upper()
        cargo_toml = CARGO_TOML_TPL.format(
            family=ufamily,
            crate=crate,
            version=VERSION,
            features=features,
            docs_features=str(CRATE_DOC_FEATURES[crate]),
        )
        readme = README_TPL.format(
            family=ufamily,
            crate=crate,
            device=devices[family][0],
            version=VERSION,
            svd2rust_version=SVD2RUST_VERSION,
            devices=make_device_rows(table, family),
        )
        lib_rs = SRC_LIB_RS_TPL.format(
            family=ufamily, mods=mods, crate=crate, svd2rust_version=SVD2RUST_VERSION
        )
        build_rs = BUILD_TPL.format(device_clauses=clauses)

        # path to output crate dir
        output_path = CWD / crate
        # path to output crate src dir
        output_src = output_path / "src"

        output_path.mkdir(exist_ok=True)
        output_src.mkdir(exist_ok=True)

        (output_path / "Cargo.toml").write_text(cargo_toml)
        (output_path / "README.md").write_text(readme)
        (output_src / "lib.rs").write_text(lib_rs)
        (output_path / "build.rs").write_text(build_rs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="Assume 'yes' to prompt", action="store_true")
    parser.add_argument("devices", help="Path to device YAML files")
    args = parser.parse_args()
    make_crates(args.devices, args.y)
