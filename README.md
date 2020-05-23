![build nightlies](https://github.com/ht32-rs/ht32-rs/workflows/build%20nightlies/badge.svg)
# HT32 Peripheral Access Crate
This repository provides Rust device support for all HT32 microcontrollers providing a safe API to that device's
peripherals using svd2rust and a community-built collection of patches to the basic SVD files. There is one crate per
device family, and each supported device is a feature-gated module in that crate. These crates are commonly known as
peripheral access crates or "PACs".

To view the generated code that makes up each crate, visit the
[ht32-rs-nightlies](https://github.com/ht32-rs/ht32-rs-nighlites) repository, which is automatically
rebuilt on every commit to ht32-rs master. The ht32-rs repository contains the patches to the underlying SVD files and
the tooling to generate the crates.

Not every register of every device will have been tested on hardware, and so errors
or omissions may remain. We can't make any guarantee of correctness. Please report any bugs you find!

## Using Device Crates In Your Own Project

In your own project's `Cargo.toml`:
```toml
[dependencies.ht32f5xxxx]
version = "0.1.0"
features = ["ht32f52342_52", "rt"]
```

The `rt` feature is optional but helpful. See
[svd2rust](https://docs.rs/svd2rust/latest/svd2rust/#the-rt-feature) for
details.

Then, in your code:

```rust
use ht32f5xxxx::ht32f52342_52;

let mut peripherals = ht32f52342_52::Peripherals::take().unwrap();
```

Refer to `svd2rust` [documentation](https://docs.rs/svd2rust) for further usage.

Replace `ht32f5xxxx` and `ht32f52342_52` with your own device.

## Using Latest "Nightly" Builds

Whenever the master branch of this repository is updated, all device crates are
built and deployed to the
[ht32-rs-nightlies](https://github.com/ht32-rs/ht32-rs-nighlites)
repository. You can use this in your `Cargo.toml`:

```toml
[dependencies.ht32f5xxxx]
git = "https://github.com/ht32-rs/ht32-rs-nighlites"
features = ["ht32f52342_52", "rt"]
```

The nightlies should always build and be as stable as the latest release, but
contain the latest patches and updates.


## Generating Device Crates / Building Locally

* Install `svd2rust`: `cargo install svd2rust`
* Install `form`: `cargo install form`
* Install rustfmt: `rustup component add rustfmt`
* Install svdtools: `pip install --user svdtools`
* Download and unzip SVD zip files: `cd svd; ./extract.sh; cd ..`
* Run the build: `./build.py`

## Helping

This project is still young and there's a lot to do!

* More peripheral patches need to be written, most of all. See what we've got
  in `peripherals/` and grab a reference manual!
* Also everything needs testing, and you can't so easily automate finding bugs
  in the SVD files...

## Releasing

Notes for maintainers:

```
$ vi scripts/makecrates.py # update version number
$ python3 scripts/makecrates.py devices/
$ vi CHANGELOG.md # add changelog entry
$ vi README.md # update version number
$ git checkout -b vX.X.X
$ git commit -am "vX.X.X"
$ git push origin vX.X.X
# wait for CI build to succeed
$ git tag -a 'vX.X.X' -m 'vX.X.X'
$ git push origin vX.X.X
$ for f in ht32f0yyy ht32f1xxxx ht32f1yyy ht32f2xxxx ht32f2yyy ht32f5xxxx ht32f5yyy ht32f6xxxx; cd $f; pwd; cargo publish --allow-dirty; cd ..; end
```
## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
dual licensed as above, without any additional terms or conditions.
