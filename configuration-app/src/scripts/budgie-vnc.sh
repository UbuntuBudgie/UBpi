#!/usr/bin/env bash
#
# Usage: budgie-vnc.sh <enable|disable|status>
#        budgie-vnc.sh <setup> <password> [subnet]
#
# setup will install service or change to the provided password
# password is required with setup parameter
#

function disable_vnc() {
  if [[ $1 -eq 1  ||  $2 -eq 1 ]]; then
    echo 'Disabling vnc service'
    systemctl --user disable --now x11vnc
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
    systemctl --user enable x11vnc --now
  fi
}

function check_vnc () {
  echo "Checking for vnc"
  if [ $(dpkg-query -W -f='${Status}' x11vnc 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    echo 'vnc not found. Installing...'
    sudo apt update && sudo apt install -y x11vnc
    if [ $(dpkg-query -W -f='${Status}' x11vnc 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
      echo "x11vnc was not installed"
      exit 1
    fi
  fi
}

function setup_vnc() {
  WARNING="--afteraccept '/usr/bin/notify-send --app-name=\"VNC Server\" \"VNC Connection\" \"Remote VNC Client connected\" -i application-x-vnc'"
  GONE="--gone '/usr/bin/notify-send --app-name=\"VNC Server\" \"VNC Connection\" \"Remote VNC Client disconnected\" -i application-x-vnc'"
  PWOPTION="-rfbauth $HOME/.config/x11vnc.pwd"
  if [ "$3" = "" ]; then
    echo "no password specified"
    exit 1
  fi
  if [[ "$3" == "--accept--" ]]; then
   PWOPTION="--accept 'zenity --question --text=\"Incoming VNC connection request. Accept?\" --title=\"VNC Connection\"'"
  fi
  if [[ "$4" == "viewonly" ]]; then
    VIEWONLY="-viewonly"
  fi
  if [[ "$5" == "localhost" ]]; then
    SUBNET="-localhost"
  elif [[ "$5" != "" ]]; then
    SUBNET="-allow $5"
  fi

  check_vnc

  SOURCEFILE=/usr/share/applications/x11vnc.desktop
  DESTFILE=$HOME/.local/share/applications/x11vnc.desktop
  if [[ ! -f "$DESTFILE" ]]; then
    if [[ -f "$SOURCEFILE" ]]; then
      cp $SOURCEFILE $DESTFILE
    fi
  fi
  if ! grep -Fxq "hidden=true" $DESTFILE; then
      echo "Hidden=true" >> $DESTFILE
  fi

  systemctl --user disable --now x11vnc

  if [[ ! -e $HOME/.config/systemd/user ]]; then
    mkdir -p $HOME/.config/systemd/user
  fi
  cp /usr/lib/budgie-desktop/arm/scripts/x11vnc.service $HOME/.config/systemd/user/
  sed -i "/ExecStart/c\ExecStart=/usr/bin/x11vnc $WARNING $GONE -repeat -forever -display :0 $VIEWONLY $SUBNET $PWOPTION" $HOME/.config/systemd/user/x11vnc.service
  x11vnc -storepasswd $3 $HOME/.config/x11vnc.pwd
  systemctl --user daemon-reload
  systemctl --user enable x11vnc
  systemctl --user start x11vnc
  echo 'Done!'
}

function vnc_status() {
  EXIT=0
  if [[ $1 -eq 1 &&  $2 -eq 1 ]]; then
    SERVICE="Enabled"
  else
    SERVICE="Disabled"
    EXIT=1
  fi
  if [ $(dpkg-query -W -f='${Status}' x11vnc 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    SERVICE="Not Installed"
    EXIT=2
  fi
  echo "VNC is $SERVICE"
  exit $EXIT
}

#if [[ "$(id -u)" -ne 0 && ! "$1" = "status" ]]; then
#  echo "You need to be root to run this."
#  exit 2
#fi

DIRNAME=$(dirname $(realpath -s $0))

systemctl --user is-active x11vnc > /dev/null 2>&1 && ACTIVE=1 || ACTIVE=0
systemctl --user is-enabled x11vnc > /dev/null 2>&1 && ENABLED=1 || ENABLED=0

if [ "$1" = "setup" ]; then
  setup_vnc $ACTIVE $ENABLED $2 $3 $4
  exit 0
elif [ "$1" = "setupgui" ]; then
  check_vnc
  python3 $DIRNAME/../vncwindow.py
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
