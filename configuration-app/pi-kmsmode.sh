#!/usr/bin/env bash

# Check if overlay_map is in correct directory, then run pibootctl

OVERLAY_DEST=/boot/firmware/overlays/overlay_map.dtb
OVERLAY_SOURCE=/boot/firmware/overlay_map.dtb

if [ "$EUID" -ne 0 ]; then
  echo "Please run with root priveleges"
  exit
fi

if ! test -f "$OVERLAY_DEST"; then
    cp $OVERLAY_SOURCE $OVERLAY_DEST
fi

pibootctl set $1
