# Ubuntu Budgie Pi4 21.04

Date 22 April 2021 **IN PREPARATION FOR RELEASE**

Hi folks,


This is our first ever release of Ubuntu Budgie for a Raspberry Pi. It is based on 21.04.

**This image is recommended only for a Pi4B or Pi400 with 4Gb/8Gb RAM.**

Just download and write to a SD Card via Gnome Disks or raspi-imager.

# Budgie ARM Tweak tool

After installation and reboot you will see our budgie-arm-config app.

Do read our [guide](https://sourceforge.net/projects/budgie-remix/files/budgie-raspi/UBPi4.pdf/download) how to use this app

By installing the package budgie-arm-environment on Intel/AMD you will see a Menu Budgie ARM application icon - run this to find your Pi IP address on your network (note the nmap issue below)


# Known issues

 1. the graphics are slightly glitchy under the default fkms. We recommend using the KMS mode for direct access displays and fkms for remote access.
 2. using the official Pi touchscreen (the one that connects via the DSI ribbon instead of HDMI) doesn't seem to work in KMS mode.  Budgie DOES load, but you get no display.  FKMS mode works fine. This is a known upstream issue https://github.com/raspberrypi/linux/issues/4020
 
----

https://discourse.ubuntubudgie.org/t/ubuntu-budgie-plans-for-raspberry-pi/4310/30?u=fossfreedom

----
