# Ubuntu Budgie Raspberry Pi Images

This directory contains the definitions used to build the Ubuntu Budgie Raspberry Pi Preinstalled Desktop image.

Image builds are performed using ubuntu-image, Canonical's official tool for building images.

- [ubuntu-image on Launchpad](https://launchpad.net/ubuntu-image)
- [ubuntu-image on GitHub](https://github.com/canonical/ubuntu-image)

## Building the image

The image can be built natively on Raspberry Pi hardware.

Install `ubuntu-image`:

```bash
sudo snap install ubuntu-image --classic
```

When building on AMD64 hosts, additional packages are required:

```bash
sudo apt install qemu-user-static binfmt-support
sudo update-binfmts --enable qemu-aarch64
```

To build our Noble 24.04 image, from this directory, run:
```bash
sudo ubuntu-image classic -O /path/to/output noble/ubuntu-budgie-noble-preinstalled-desktop-arm64+raspi.yaml
```

The generated image file will be written to the specified output directory.
