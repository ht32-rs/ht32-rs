# HT32 Peripheral Access Crates - Nightly Builds

This repository contains automated builds of the [ht32-rs] crates, rebuilt
whenever a PR is merged to the master branch. Consult the [ht32-rs] README
for full details.

[ht32-rs]: https://github.com/ht32-rs/ht32-rs

## Using These Builds

Edit your `Cargo.toml`:

```toml
[dependencies.ht32f5xxxx]
version = "0.1.0"
features = ["ht32f52342_52", "rt"]
```

The nightlies should always build and be as stable as the latest release, but
typically with the latest patches and updates.


