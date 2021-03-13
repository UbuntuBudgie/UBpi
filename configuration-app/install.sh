#!/bin/bash

ROOT_UID=0
PREFIX_DIR=""

# PREFIX_DIRination directory
if [ "$UID" -eq "$ROOT_UID" ]; then
  PREFIX_DIR=""
else
  PREFIX_DIR="."
fi

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -d|--dest)
      PREFIX_DIR="${2}"
      if [[ ! -d "${PREFIX_DIR}" ]]; then
        echo "ERROR: prefix destination directory does not exist."
        exit 1
      fi
      shift 2
      ;;
  esac
done

mkdir -p ${PREFIX_DIR}/usr/share/budgie-desktop/layouts
mkdir -p ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
mkdir -p ${PREFIX_DIR}/usr/share/glib-2.0/schemas
mkdir -p ${PREFIX_DIR}/etc/xdg/autostart
mkdir -p ${PREFIX_DIR}/usr/share/applications


cp ubuntubudgiecompact.layout ${PREFIX_DIR}/usr/share/budgie-desktop/layouts
cp reset.sh ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
cp budgie-xrdp.sh ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
cp budgie-ssh.sh ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
cp pi-kmsmode.sh ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
cp *.py ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
glib-compile-resources org.ubuntubudgie.armconfig.gresource.xml
cp *.gresource ${PREFIX_DIR}/usr/lib/budgie-desktop/arm
cp org.ubuntubudgie.armconfig.gschema.xml ${PREFIX_DIR}/usr/share/glib-2.0/schemas/
glib-compile-schemas ${PREFIX_DIR}/usr/share/glib-2.0/schemas/
cp budgie-armconfig-autostart.desktop ${PREFIX_DIR}/etc/xdg/autostart
cp budgie-armconfig.desktop ${PREFIX_DIR}/usr/share/applications
