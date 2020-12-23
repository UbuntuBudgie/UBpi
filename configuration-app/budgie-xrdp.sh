#!/usr/bin/env bash
#
# Usage: budgie-xrdp.sh [enable|disable|status]
#
# enable / disable require sudo priveleges
# status does NOT require sudo priveleges 


function disable_xrdp() {
  if [ $2 -eq 1 ]; then
    echo 'Disabling xrdp service'
    systemctl disable xrdp
  else
    echo 'xrdp already disabled'
  fi
  
  if [ $1 -eq 1 ]; then
    echo 'Stopping xrdp service'
    systemctl stop xrdp
  else
    echo 'xrdp not running'
  fi
  echo 'Done!'
}

function enable_xrdp() {
  echo "Checking for xrdp"
  if [ $(dpkg-query -W -f='${Status}' xrdp 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    echo 'xrdp not found. Installing...'
    apt install -y xrdp
    systemctl enable xrdp
  else
    echo 'xrdp already installed!'
  fi

  echo 'Checking if xrdp is enabled'
  if [ $2 -eq 1 ]; then
    echo 'xrdp already enabled!'
  else
    echo 'Enabling xrdp'
    systemctl enable xrdp
  fi

  echo 'Checking if xrdp is running'
  if [ $1 -eq 1 ]; then
    echo 'xrdp already started!'
  else
    echo 'Starting xrdp'
    systemctl start xrdp
  fi

  echo 'Checking configuration file'
  sed -e '/\/etc\/X11\/Xsession/ s/^#*/#/g' -i $FILE
  if ! grep -Fxq "budgie-desktop" $FILE; then 
    echo 'budgie-desktop' >> $FILE
  fi

  echo 'Restarting xrdp service'
  systemctl restart xrdp
  echo 'Done!'
}

function xrdp_status() {
  if [ $1 -eq 1 ]; then
    STARTED="started"
  else
    STARTED="stopped"
  fi

  if [ $2 -eq 1 ]; then
    SERVICE="enabled"
  else
    SERVICE="disabled"
  fi
  if [ $(dpkg-query -W -f='${Status}' xrdp 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    INSTALLED="missing"
  else
    INSTALLED="installed"
  fi

  echo "xrdp package is $INSTALLED"
  echo "xrdp service is $STARTED and $SERVICE"
}

if [[ "$(id -u)" -ne 0 && ! "$1" = "status" ]]; then
  echo "You need to be root to run this."
  exit 1
fi

FILE='/etc/xrdp/startwm.sh'
STATUS=$(systemctl status xrdp 2>/dev/null)

[[ $(echo $STATUS | grep -c " active") -ne 0 ]] && ACTIVE=1 || ACTIVE=0
[[ $(echo $STATUS | grep -c "xrdp.service; enabled") -ne 0 ]] && ENABLED=1 || ENABLED=0

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
  exit 1
fi

