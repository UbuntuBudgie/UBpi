#!/usr/bin/env bash
#
# Usage: budgie-vnc.sh <enable|disable|status>
#        budgie-vnc.sh <setup> <password> [subnet]
#
# setup will install service or change to the provided password
# password is required with setup parameter 
#
# enable / disable require sudo privileges
# status does NOT require sudo privileges 

function disable_vnc() {
  if [[ $1 -eq 1  ||  $2 -eq 1 ]]; then
    echo 'Disabling vnc service'
    systemctl stop x11vnc
  else
    echo 'vnc already disabled'
  fi
}

function enable_vnc() {
  echo 'Checking if vnc is enabled'
  if [[ $1 -eq 1  &&  $2 -eq 1 ]]; then
    echo 'vnc already enabled!'
  else
    echo 'Enabling vnc'
    systemctl enable x11vnc --now
  fi
}

function setup_vnc() {
  if [ "$3" = "" ]; then
    echo "no password specified"
    exit 1
  fi
  if [ "$4" != "" ]; then
    SUBNET="-allow $4"
  fi
  echo "Checking for vnc"
  if [ $(dpkg-query -W -f='${Status}' x11vnc 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    echo 'vnc not found. Installing...'
    apt update
    apt install -y x11vnc
    echo "Hidden=true" >> /usr/share/applications/x11vnc.desktop
  else
    systemctl disable x11vnc --now
  fi
  cp /usr/lib/budgie-desktop/arm/x11vnc.service /etc/systemd/system/
  sed -i "/ExecStart/c\ExecStart=/usr/bin/x11vnc -repeat -forever -display :0 $SUBNET -rfbauth /etc/x11vnc.pwd" /etc/systemd/system/x11vnc.service
  x11vnc -storepasswd $3 /etc/x11vnc.pwd
  chmod a+r /etc/x11vnc.pwd
  systemctl daemon-reload
  systemctl enable x11vnc
  systemctl start x11vnc
  echo 'Done!'
}

function vnc_status() {
  EXIT=0
  if [[ $1 -eq 1 &&  $2 -eq 1 ]]; then
    SERVICE="active"
  else
    SERVICE="inactive"
    EXIT=1
  fi
  if [ $(dpkg-query -W -f='${Status}' x11vnc 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    INSTALLED="not installed"
    EXIT=1
  else
    INSTALLED="installed"
  fi
  echo "vnc is $INSTALLED"
  echo "vnc service is $SERVICE"
  exit $EXIT
}

if [[ "$(id -u)" -ne 0 && ! "$1" = "status" ]]; then
  echo "You need to be root to run this."
  exit 2
fi

systemctl is-active x11vnc > /dev/null 2>&1 && ACTIVE=1 || ACTIVE=0
systemctl is-enabled x11vnc > /dev/null 2>&1 && ENABLED=1 || ENABLED=0

if [ "$1" = "setup" ]; then
  setup_vnc $ACTIVE $ENABLED $2 $3
  exit 0
elif [ "$1" = "enable" ]; then
  enable_vnc $ACTIVE $ENABLED
  exit 0
elif [ "$1" = "disable" ]; then
  disable_vnc $ACTIVE $ENABLED
  exit 0
elif [ "$1" = "status" ]; then
  vnc_status $ACTIVE $ENABLED
  exit 0
else
  echo "Usage: budgie-vnc <enable|disable|status>"
  echo "     : budgie-vnc <setup> <password> [subnet]"
  vnc_status $ACTIVE $ENABLED
  exit 2
fi
