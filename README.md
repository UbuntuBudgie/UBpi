# Ubuntu Budgie Pi4 23.10

[![](https://opencollective.com/ubuntubudgie/tiers/backer.svg?avatarHeight=96)](https://opencollective.com/ubuntubudgie)

Date: 22 August 2023

Hi folks,

This is our Raspberry Pi build based upon 23.10 - it is of alpha quality to be used for feedback and testing.

https://discourse.ubuntubudgie.org/t/testing-23-10-are-you-brave-enough/6699

Please be sure to read the list of known issues.

**This image is recommended only for a Pi4B or Pi400 with 2Gb/4Gb/8Gb RAM.**

Just download and write to a SD Card via Gnome Disks or raspi-imager.

# Budgie ARM Tweak tool

After installation and reboot you will see our budgie-arm-config app.

Do read our [guide](https://sourceforge.net/projects/budgie-remix/files/budgie-raspi-21.04/UBPi4.pdf/download) how to use this app

By installing the package budgie-arm-environment on Intel/AMD you will see a Menu Budgie ARM application icon - run this to find your Pi IP address on your network (note the nmap issue below)

# Optimisations

The following optimisations are optional:

First use the tweak tool and ensure you are booting at 2Ghz.  You should only use this option if you are using a decent heatsink - preferably with a good fan.

The other options below apply to the 8Mb raspi model.

We are going to speed up our system and extend our microSD card’s life by using our 8GB of ram as much as possible. This includes moving some parts of our filesystem in ramdisks, and using Preload to speed up our system a bit.

First we are going to move our temporary folders and logs folder to ramdisk. Ramdisks are basically filesystems created in ram. They won’t wear down our microSD, and they are super fast.

The catch is, everything there is lost on reboot. In our case, we don’t really care. /tmp and /var/tmp are temporary folders and they are not really meant to store anything important anyway.

/var/log is actually one of the places where our operative system writes all the time, and we want to avoid that. Assuming you dont want to check logs after a reboot, using ramdisk can help massively.

Let’s edit our fstab first and add the lines below.

    nano /etc/fstab

Add the 3 lines at the end.

    tmpfs /tmp tmpfs defaults,noatime,nosuid,size=500m 0 0
    tmpfs /var/tmp tmpfs defaults,noatime,nosuid,size=500m 0 0
    tmpfs /var/log tmpfs defaults,noatime,nosuid,mode=0755,size=500m 0 0

NOTE: size=500m means each ramdisk is limited to a maximum of 500MB of ram used. It is not going to use 500MB of ram on system start though, so higher values are safer in my opinion. We have plenty of ram on this Raspberry PI 4B 8GB and Ubuntu Budgie is quite lightweight.

Next 8Gb model optimisation suggestion - using Preload

Next, we really want to make good use of all that ram to speed up the system a bit. Preload will learn libraries and applications you use the most, and load those in RAM when we boot our systems. Sure, there is a tradeoff, reboots will be slower. But using the system will be a bit faster. If you don’t really plan to reboot all the time, take this as a win.

First, Install preload.

    sudo apt-get install preload

Once installed, let’s go and change some of the settings to make it a bit more aggressive loading libraries and applications in ram.

Let’s open preload configuration file.

    sudo nano /etc/preload.conf

These are the lines you can modify

    minsize 100000
    mapprefix = !/var/log;!/dev;!/var/tmp;!/tmp;/
    exeprefix = !/var/log;!/dev;!/var/tmp;!/tmp;/
    autosave = 360
    sortstrategy = 0

Reboot and test

That should be enough tweaks for now. Time for a good old reboot. Fingers crossed.

# Known issues

1. The default image currently does not ship with universe and multiverse repositories enabled. Therefore, you will encounter issues installing software from these repos. As a workaround, simply run Software Sources (or software-properties-gtk from terminal) and enable these from the Ubuntu Software tab

2. Various kernel modules have been moved from the linux-modules-raspi package in order to reduce the initramfs size. This results in several applications (i.e. Docker, zram) failing due to missing kernel modules. To work around this:

    sudo apt install linux-modules-extra-raspi

3. When using the auto-login option, gnome keyring may not be allowed, causing issues if you are using remote access options that require a password to connect. You can disable the password by installing seahorse:

    sudo apt install seahorse

and change the change the password to a blank password. This will store ALL passwords unencrypted, and will work around this issue. However, if you have any sensitive passwords stored, or the device is shared by multiple users, its a convenience vs. security tradeoff.

4. After the initial setup, the Sharing panel of Budgie Control Center may freeze on first use. Rebooting after the initial setup avoids this issue.

Please feedback via our discourse forum https://discourse.ubuntubudgie.org

----
