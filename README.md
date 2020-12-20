# UBpi
Ubuntu Budgie for the Raspberry Pi 4

----

In development - intrepid users only!

Recommendation - Pi4 with 4GB minimum
Use a good quality Class 10 microSD card with min 32GB

To create your own image - recommend use Ubuntu Budgie 20.04 or later

Git clone this repo

run

    chmod +x budgie-setup.sh
    ./budgie-setup.sh

When its completed you will have a .img file to write to your Pi 4

Notes:

The build will pause waiting for the plymouth theme to choose - do not use the budgie scale-2 theme
seed.yaml needs to be updated to use the latest arm snap numbers

After running the scripts reboot your host computer.