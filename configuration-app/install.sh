#!/usr/bin/env bash

sudo cp ubuntubudgiecompact.layout /usr/share/budgie-desktop/layouts
sudo mkdir -p /usr/lib/budgie-desktop/arm
sudo cp reset.sh /usr/lib/budgie-desktop/arm
sudo cp *.py /usr/lib/budgie-desktop/arm
gcompile-resources org.ubuntubudgie.armconfig.gresource.xml
sudo cp *.gresource /usr/lib/budgie-desktop/arm
sudo cp org.ubuntubudgie.armconfig.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/ 
sudo cp budgie-armconfig-autostart.desktop /etc/xdg/autostart
sudo cp budgie-armconfig.desktop /usr/share/applications
