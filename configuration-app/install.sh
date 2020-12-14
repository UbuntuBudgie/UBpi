#!/usr/bin/env bash

PREFIX_DIR=""

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -d|--dest)
      PREFIX_DIR="${2}"
      if [[ ! -d "${dest}" ]]; then
        echo "ERROR: Destination directory does not exist."
        exit 1
      fi
      shift 2
      ;;
  esac
done

sudo mkdir -p ${dest}/usr/share/budgie-desktop/layouts
sudo mkdir -p ${dest}/usr/lib/budgie-desktop/arm
sudo mkdir -p ${dest}/usr/share/glib-2.0/schemas
sudo mkdir -p ${dest}/etc/xdg/autostart


sudo cp ubuntubudgiecompact.layout ${dest}/usr/share/budgie-desktop/layouts
sudo cp reset.sh ${dest}/usr/lib/budgie-desktop/arm
sudo cp *.py ${dest}/usr/lib/budgie-desktop/arm
glib-compile-resources org.ubuntubudgie.armconfig.gresource.xml
sudo cp *.gresource ${dest}/usr/lib/budgie-desktop/arm
sudo cp org.ubuntubudgie.armconfig.gschema.xml ${dest}/usr/share/glib-2.0/schemas/
sudo glib-compile-schemas ${dest}/usr/share/glib-2.0/schemas/
sudo cp budgie-armconfig-autostart.desktop ${dest}/etc/xdg/autostart
sudo cp budgie-armconfig.desktop ${dest}/usr/share/applications
