# Ubuntu Budgie Pi4 21.04

Release Date 22 April 2021

Downloading: Note Sourceforge can & will take several days and weeks to spin out to all its mirrors.  So in the
early days a direct download of the .xz file may take a long-long-long time.

Do use the torrent - but please do seed the torrent after download to ensure everyone after you benefits as well

----

Hi folks,

This is our first ever release of Ubuntu Budgie for a Raspberry Pi. It is based on 21.04.

**This image is recommended only for a Pi4B or Pi400 with 4Gb/8Gb RAM.**

Just download and write to a Class 10 SD Card or SSD/NVME (recommended) via Gnome Disks or raspi-imager.

# Budgie ARM Tweak tool

After installation and reboot you will see our budgie-arm-config app.

Do read our [downloadable guide](https://sourceforge.net/projects/budgie-remix/files/budgie-raspi/UBPi4.pdf/download) how to use this app

By installing the package budgie-arm-environment on Intel/AMD you will see a Menu Budgie ARM application icon - run this to find your Pi IP address on your network (note the nmap issue below)


# Known issues

 1. the graphics are slightly glitchy using fkms for direct access displays. We recommend using the KMS mode for direct access displays.
 2. The Tweak Tool displays tab text states "fkms" is the default.  For 21.04 it is in-fact KMS that is the default.
 3. using the official Pi touchscreen (the one that connects via the DSI ribbon instead of HDMI) doesn't seem to work in KMS mode.  Budgie DOES load, but you get no display.  FKMS mode works fine. This is a known upstream issue https://github.com/raspberrypi/linux/issues/4020
 4. when installing on a Compute Module 4, using the Pi Foundation's IO Board, the USB ports may not be working. This is due to the DWC2 USB2 controller not being in host mode by default. If you are affected by this, it can be resolved by editing /boot/firmware/config.txt from another device, and adding 
 `dtoverlay=dwc2,dr_mode=host`
 5. The 21.04 repositories does not have an ARM64 package for Kodi - https://discourse.ubuntubudgie.org/t/psa-how-to-install-kodi-on-21-04-raspberry-pi/4909
 6. When rebooting sound config goes back to jack - https://discourse.ubuntubudgie.org/t/when-rebooting-sound-config-goes-back-to-jack/4907

----

For support queries https://discourse.ubuntubudgie.org

For help to develop the Tweak Tool https://github.com/ubuntubudgie/ubpi

Release Notes https://ubuntubudgie.org/2021/03/release-notes-ubuntu-budgie-21-04-on-a-raspberry-pi-4/
----
