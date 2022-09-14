#!/usr/bin/env bash
#
# Usage: budgie-ssh.sh [enable|disable|status]
#
# enable / disable require sudo privileges
# status does NOT require sudo privileges

function disable_ssh() {
  if [[ $1 -eq 1  ||  $2 -eq 1 ]]; then
    echo 'Disabling ssh service'
    systemctl disable ssh --now
  else
    echo 'ssh already disabled'
  fi
}

function enable_ssh() {
  echo "Checking for ssh"
  if [ $(dpkg-query -W -f='${Status}' openssh-server 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    echo 'ssh not found. Installing...'
    apt install -y openssh-server
    systemctl enable ssh --now
  else
    echo 'ssh already installed!'
    echo 'Checking if ssh is enabled'
    if [[ $1 -eq 1  &&  $2 -eq 1 ]]; then
      echo 'ssh already enabled!'
    else
      echo 'Enabling ssh'
      systemctl enable ssh --now
    fi
  fi

  echo 'Done!'
}

function ssh_status() {
  EXIT=0
  if [[ $1 -eq 1 &&  $2 -eq 1 ]]; then
    SERVICE="Enabled"
    EXIT=0
  else
    SERVICE="Disabled"
    EXIT=1
  fi
  if [ $(dpkg-query -W -f='${Status}' openssh-server 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    SERVICE="Not Installed"
    EXIT=2
  fi
  echo "SSH is $SERVICE"
  exit $EXIT
}

if [[ "$(id -u)" -ne 0 && ! "$1" = "status" ]]; then
  echo "You need to be root to run this."
  exit 2
fi

FILE='/etc/xrdp/startwm.sh'

systemctl is-active ssh > /dev/null 2>&1 && ACTIVE=1 || ACTIVE=0
systemctl is-enabled ssh > /dev/null 2>&1 && ENABLED=1 || ENABLED=0

if [ "$1" = "enable" ]; then
  enable_ssh $ACTIVE $ENABLED
  exit 0
elif [ "$1" = "disable" ]; then
  disable_ssh $ACTIVE $ENABLED
  exit 0
elif [ "$1" = "status" ]; then
  ssh_status $ACTIVE $ENABLED
  exit 0
else
  echo "Usage: budgie-ssh [enable|disable|status]"
  ssh_status $ACTIVE $ENABLED
  exit 2
fi
