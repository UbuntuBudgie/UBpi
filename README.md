# Ubuntu Budgie Pi4 22.04.3

Date 10th August 2023

We are pleased to announce the release of the next version of our distro, the third 22.04 LTS point release.

The LTS version is supported for 3 years while the regular releases are supported for 9 months.

The new release rolls-up various fixes and optimizations by Ubuntu Budgie team, that have been released since the 22.04.2 release in February:

* Budgie Welcome updates include lots more translation updates
* various bug fixes for our budgie-applets known as budgie-extras
* new version of budgie-analogue-clock-applet
* brand new fluent based makeover including fluent-gtk-theme and fluent-icon-theme
* new version of mcmojave-circle icon theme
* ability to add nemo-terminal to the file-manager
* new version of tela-circle-icon-theme
* new version of whitesur-icon-theme

We also inherit hundreds of stability, bug-fixes and optimizations made to the underlying Ubuntu repositories. Many thanks to all the volunteers, Debian & Ubuntu maintainers and Canonical employees who have done such a sterling job packaging the changes that many more developers from all over the world have resolved. The power of FOSS that we are all proud to be part of.

You can read more about 22.04 via our [Release Notes](https://discourse.ubuntu.com/t/jammy-jellyfish-release-notes/24668)

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

1. The graphics are slightly glitchy under fkms. We recommend using the KMS mode for direct access displays and fkms for remote access.


Please feedback via our discourse forum https://discourse.ubuntubudgie.org

----
