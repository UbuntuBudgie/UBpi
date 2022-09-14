#!/usr/bin/env bash
#
# Usage: budgie-xrdp.sh [enable|disable|status]
#
# enable / disable require sudo priveleges
# status does NOT require sudo priveleges

function disable_xrdp() {
  if [[ $1 -eq 1  ||  $2 -eq 1 ]]; then
    echo 'Disabling xrdp service'
    systemctl disable --now xrdp
  else
    echo 'xrdp already disabled'
  fi
}

function enable_xrdp() {
  echo "Checking for xrdp"
  if [ $(dpkg-query -W -f='${Status}' xrdp 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    echo 'xrdp not found. Installing...'
    apt install -y xrdp
    systemctl enable --now xrdp
  else
    echo 'xrdp already installed!'
    echo 'Checking if xrdp is enabled'
    if [[ $1 -eq 1  &&  $2 -eq 1 ]]; then
      echo 'xrdp already enabled!'
    else
      echo 'Enabling xrdp'
      systemctl enable --now xrdp
    fi
  fi

  echo 'Checking configuration file'
  echo $FILE
  sed -e '/\/etc\/X11\/Xsession/ s/^#*/#/g' -i $FILE
  if ! grep -Fxq "budgie-desktop" $FILE; then
    echo 'budgie-desktop' >> $FILE
    echo 'Restarting xrdp service'
    systemctl restart xrdp
  fi
  echo 'Done!'
}

function xrdp_status() {
  EXIT=0
  if [[ $1 -eq 1 &&  $2 -eq 1 ]]; then
    SERVICE="Enabled"
  else
    SERVICE="Disabled"
    EXIT=1
  fi
  if [ $(dpkg-query -W -f='${Status}' xrdp 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    SERVICE="Not Installed"
    EXIT=2
  fi
  echo "XRDP is $SERVICE"
  exit $EXIT
}

if [[ "$(id -u)" -ne 0 && ! "$1" = "status" ]]; then
  echo "You need to be root to run this."
  exit 2
fi

FILE='/etc/xrdp/startwm.sh'

systemctl is-active xrdp > /dev/null 2>&1 && ACTIVE=1 || ACTIVE=0
systemctl is-enabled xrdp > /dev/null 2>&1 && ENABLED=1 || ENABLED=0

if [ ! -f "$FILE" ]; then
  ENABLED=0
elif ! grep -q budgie $FILE; then
  ENABLED=0
fi

if [ "$1" = "enable" ]; then
  enable_xrdp $ACTIVE $ENABLED
  exit 0
elif [ "$1" = "disable" ]; then
  disable_xrdp $ACTIVE $ENABLED
  exit 0
elif [ "$1" = "status" ]; then
  xrdp_status $ACTIVE $ENABLED
  exit 0
else
  echo "Usage: budgie-xrdp [enable|disable|status]"
  xrdp_status $ACTIVE $ENABLED
  exit 2
fi
