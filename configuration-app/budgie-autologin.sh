#!/usr/bin/env bash

FILE=/etc/lightdm/lightdm.conf
if [ ! -f "$FILE" ]; then
    echo "[Seat:*]" > $FILE
    echo "autologin-guest=false" >> $FILE
    echo "autologin-user=" >> $FILE
    echo "autologin-user-timeout=0" >> $FILE
fi

grep -q "autologin-user=*" $FILE && sed -i "s/^autologin-user=.*/autologin-user=$1/" $FILE || echo "autologin-user=$1" >> $FILE
