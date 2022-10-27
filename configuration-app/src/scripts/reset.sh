#!/usr/bin/env bash

key="/com/solus-project/budgie-panel/instance/budgie-menu/"
instance=$(dconf dump /com/solus-project/budgie-panel/applets/ | grep -B 3 'Budgie Menu' | awk -F"[" '{print $2'} | awk -F"]" '{print $1}' | grep "{")

if [ "$1" != "true" ] && [ "$1" != "false" ]; then
   echo "Missing argument: true | false"
   exit 1
fi

if [ "$instance" != "" ]; then
   echo "Found schema key :$instance"
   gsettings set com.solus-project.budgie-menu:$key$instance/ menu-compact $1
else
   echo "Budgie Menu does not seem to be in panel"
fi