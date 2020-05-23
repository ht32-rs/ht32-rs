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

import os
import glob
import os.path
import argparse
import yaml

VERSION = "0.1.0"
SVD2RUST_VERSION = "0.17.0"

CRATE_DOC_FEATURES = {
    "ht32f0yyy": ["rt", "ht32f0006", "ht32f0008"],
    "ht32f1xxxx": ["rt", "ht32f12345", "ht32f12364", "ht32f12365_66"],
    "ht32f1yyy": ["rt", "ht32f125x", "ht32f1653_54",  "htf32f1655_56", "ht32f175x"],
    "ht32f2xxxx": ["rt", "ht32f22366"],
    "ht32f2yyy": ["rt", "ht32f275x"],
    "ht32f5xxxx": ["rt", "ht32f50220_30", "ht32f50231_41", "ht32f50343", "ht32f52142",
                    "ht32f52220_30", "ht32f52231_41", "ht32f52243_53", "ht32f52331_41",
                    "ht32f52342_52", "þ32f52344_54", "ht32f52357_67", "ht32f57331_41",
                    "ht32f57342_52", "ht32f59041", " ht32f59741"],
    "ht32f5yyy": ["rt", "ht32f5826"],
    "ht32f6xxxx": ["rt", "ht32f61352", "ht32f65230_40"],
}

CARGO_TOML_TPL = """\
[package]
edition = "2018"
name = "{crate}"
version = "{version}"
authors = ["Henrik Böving <hargonix@gmail.com>", "ht32-rs Contributors"]
description = "Device support crates for {family} devices"
repository = "https://github.com/ht32-rs/ht32-rs"
readme = "README.md"
keywords = ["ht32", "svd2rust", "no_std", "embedded"]
categories = ["embedded", "no-std"]
license = "MIT/Apache-2.0"

[dependencies]
bare-metal = "0.2.4"
vcell = "0.1.0"
cortex-m = ">=0.5.8,<0.7"

[dependencies.cortex-m-rt]
optional = true
version = "0.6.10"

[package.metadata.docs.rs]
features = {docs_features}
targets = []

[features]
default = []
rt = ["cortex-m-rt/device"]
{features}
"""

SRC_LIB_RS_TPL = """\
//! Peripheral access API for {family} microcontrollers
//! (generated using [svd2rust](https://github.com/rust-embedded/svd2rust)
//! {svd2rust_version})
//!
//! You can find an overview of the API here:
//! [svd2rust/#peripheral-api](https://docs.rs/svd2rust/{svd2rust_version}/svd2rust/#peripheral-api)
//!
//! For more details see the README here:
//! [ht32-rs](https://github.com/ht32-rs/ht32-rs)
//!
//! This crate supports all {family} devices; for the complete list please
//! see:
//! [{crate}](https://github.com/ht32-rs/ht32-rs/tree/master/{crate})
//!

#![no_std]

mod generic;
pub use self::generic::*;

{mods}
"""

README_TPL = """\
# IS THIS THE CRATE I AM SEARCHING FOR
Note that Holtek has 2 chip naming regulations, one with 4 digits, the other with 5.
Crates that are generated for 4 digits ones have a naming scheme like HT32F1yyy,
the ones for 5 digits HT32F1xxxx. You should make sure this is the crate you are
searching for.

# {crate}
This crate provides an autogenerated API for access to {family} peripherals.
The API is generated using [svd2rust] with patched svd files containing
extensive type-safe support. For more information please see the [main repo].

Refer to the [documentation] for full details.

[svd2rust]: https://github.com/japaric/svd2rust
[main repo]: https://github.com/ht32-rs/ht32-rs
[documentation]: https://docs.rs/{crate}/latest/{crate}/

## Usage
Each device supported by this crate is behind a feature gate so that you only
compile the device(s) you want. To use, in your Cargo.toml:

```toml
[dependencies.{crate}]
version = "{version}"
features = ["{device}", "rt"]
```

The `rt` feature is optional and brings in support for `cortex-m-rt`.

In your code:

```rust
use {crate}::{device};

let mut peripherals = {device}::Peripherals::take().unwrap();
let gpioa = &peripherals.GPIOA;
gpioa.odr.modify(|_, w| w.odr0().set_bit());
```

For full details on the autogenerated API, please see:
https://docs.rs/svd2rust/{svd2rust_version}/svd2rust/#peripheral-api

## Supported Devices

| Module | Devices | Links |
|:------:|:-------:|:-----:|
{devices}
"""


BUILD_TPL = """\
use std::env;
use std::fs;
use std::path::PathBuf;
fn main() {{
    if env::var_os("CARGO_FEATURE_RT").is_some() {{
        let out = &PathBuf::from(env::var_os("OUT_DIR").unwrap());
        println!("cargo:rustc-link-search={{}}", out.display());
        let device_file = {device_clauses};
        fs::copy(device_file, out.join("device.x")).unwrap();
        println!("cargo:rerun-if-changed={{}}", device_file);
    }}
    println!("cargo:rerun-if-changed=build.rs");
}}
"""


def read_device_table():
    path = os.path.join(
        os.path.abspath(os.path.split(__file__)[0]), os.pardir,
        "ht32_part_table.yaml")
    with open(path, encoding='utf-8') as f:
        table = yaml.safe_load(f)
    return table


def make_device_rows(table, family):
    rows = []
    for device, dt in table[family].items():
        links = "[{}]({}), [st.com]({})".format(
            dt['um'], dt['um_url'], dt['url'])
        members = ", ".join(m for m in dt['members'])
        rows.append("| {} | {} | {} |".format(device, members, links))
    return "\n".join(sorted(rows))


def make_features(devices):
    return "\n".join("{} = []".format(d) for d in sorted(devices))


def make_mods(devices):
    return "\n".join('#[cfg(feature = "{0}")]\npub mod {0};\n'.format(d)
                     for d in sorted(devices))


def make_device_clauses(devices):
    return " else ".join("""\
        if env::var_os("CARGO_FEATURE_{}").is_some() {{
            "src/{}/device.x"
        }}""".strip().format(d.upper(), d) for d in sorted(devices)) + \
            " else { panic!(\"No device features selected\"); }"


def main(devices_path, yes):
    devices = {}

    for path in glob.glob(os.path.join(devices_path, "*.yaml")):
        yamlfile = os.path.basename(path)
        family_string = yamlfile.split(".")[0].split("_")[0]
        family = family_string[:6]
        if len(family_string) == 10:
            family += 4 * "x"
        elif len(family_string) == 9:
            family += 3 * "y"
        else:
            print(f"The yaml file name '{yamlfile}' does not fit the format we expect")
            exit(1)
        device = os.path.splitext(yamlfile)[0].lower()
        if family not in devices:
            devices[family] = []
        devices[family].append(device)

    table = read_device_table()

    dirs = ", ".join(x.lower()+"/" for x in devices)
    print("Going to create/update the following directories:")
    print(dirs)
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
            family=ufamily, crate=crate, version=VERSION, features=features,
            docs_features=str(CRATE_DOC_FEATURES[crate]))
        readme = README_TPL.format(
            family=ufamily, crate=crate, device=devices[family][0],
            version=VERSION, svd2rust_version=SVD2RUST_VERSION,
            devices=make_device_rows(table, family))
        lib_rs = SRC_LIB_RS_TPL.format(family=ufamily, mods=mods, crate=crate,
                                       svd2rust_version=SVD2RUST_VERSION)
        build_rs = BUILD_TPL.format(device_clauses=clauses)

        os.makedirs(os.path.join(crate, "src"), exist_ok=True)
        with open(os.path.join(crate, "Cargo.toml"), "w") as f:
            f.write(cargo_toml)
        with open(os.path.join(crate, "README.md"), "w") as f:
            f.write(readme)
        with open(os.path.join(crate, "src", "lib.rs"), "w") as f:
            f.write(lib_rs)
        with open(os.path.join(crate, "build.rs"), "w") as f:
            f.write(build_rs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="Assume 'yes' to prompt",
                        action="store_true")
    parser.add_argument("devices", help="Path to device YAML files")
    args = parser.parse_args()
    main(args.devices, args.y)
