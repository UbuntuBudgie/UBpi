"""
Budgie Pi Configuration App
Copyright © 2021-2022 Ubuntu Budgie Developers
Website=https://ubuntubudgie.org
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version. This
program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details. You
should have received a copy of the GNU General Public License along with this
program.  If not, see <https://www.gnu.org/licenses/>.
"""


# General
AUTOSTART = "Enable or disable autostart of the configuration tool"

# Layouts Tab
LAYOUTS_TAB = "Configure different display options for smaller screens"
STANDARD_RES = ("Recommended for screens with\n"
                "vertical resolutions of 900 and above")
COMPACT_RES = ("Recommended for small screens with\n"
               "vertical resolutions of at least 768")
MINI_RES = ("Recommended for small screens with\n"
            "vertical resolutions of less than 768")
APPLY_LAYOUT = ("Apply the new layout.\n"
                "Logout/Login required to complete")

# Overclock Tab
OVERCLOCK_TAB = "Configure clock speed and view CPU temperature"
CPU_TEMP = ("Current CPU temperature. The Pi will throttle at temperatures "
            "around 80°C. Overclocking may affect the throttle temp.")
CPU_SPEEDS = ("Higher speeds will increase performance, but may increase "
              "heat or cause instability. Pi400 cannot be set below 1.8GHz")
SPEED_BUTTON = ("Apply the new clock speed.\n"
                "The new speed will take effect after reboot")
NO_CONFIGTXT = ("File '/boot/firmware/config.txt' not found.\n"
                "Overclock disabled - Is this a valid Pi?")

# Remote Tab
REMOTE_TAB = "Options to configure remote access to this device"
REFRESH_IP = ("Updates the IP if you have changed connection\n"
              "method, or connected to a new network.")
FINDMYPI_SERVER = ("Enable FindMyPi UDP server on app startup. This is not "
                   "needed when using nmap on the client")
AUTOLOGIN = ("Enable automatic login, and disable the lock screen to avoid "
             "issues with remote access. See Release Notes for more info.")
XRDP_BUTTON = ("Enable / disable Budgie Pi's XRDP access. This should not "
               "be used when Gnome's RDP is enabled.")
XRDP_NOT_INSTALLED = ("Budgie Pi provides an alternative xrdp option.\n"
                      "This will install the xrdp package.")
SSH_BUTTON = ("Enable or disable SSH access (Remote Login) through Budgie "
              "Control Center Sharing options.")
SSH_NOT_INSTALLED = ("SSH access is not currently available. This will "
                     "install OpenSSH to enable this option in Budgie Desktop "
                     "Settings.")
VNC_BUTTON = ("Enable VNC access to this device, VNC allows screen sharing. "
              "Enabling / Disabling VNC may take a minute to complete.")
VNC_NOT_INSTALLED = ("Budgie Pi provides an alternative vnc option.\n"
                     "This will install the x11vnc package.")

# Display Tab
DISPLAY_TAB = "Configure Video Modes and Video Memory"
VIDEO_MODE = ("KMS mode is recommended for attached displays. FKMS is "
              "recommended for remote access. Legacy is non-accelerated.")
GPU_MEMORY = ("Select the amout of memory to reserve for video usage. Too "
              "large a value may hurt performance if it is not needed.")
UPDATE_VIDEO = ("Apply the selected video mode\nReboot required for changes "
                "to take effect")
UPDATE_MEMORY = ("Apply the selected memory setting\n"
                 "Reboot required for changes to take effect")
NO_PIBOOTCTL = ("Unable to make changes to the Display options.\n"
                "This is not a Pi, or pibootctl may not be installed.")

# Findmypi
NMAP_BUTTON = ("When enabled, nmap is used to scan the network for Pis.\n"
               "If disabled, it scans for Pis running the FindMyPi server.")
REFRESH_BUTTON = "Rescan the network for Raspberry Pis"
COPYIP_BUTTON = "Copy the currently selected IP address to the clipboard"
SSH_FINDPI = "Open a SSH connection to the selected machine"
SSH_ENTRY = "Enter the username you wish to use for the SSH session"


def add(widget, label, status):
    widget.connect("enter-notify-event", set_label, label, status)
    widget.connect("leave-notify-event", clear_label, label)


def set_label(widget, event, label, status):
    label.set_text(status)


def clear_label(widget, event, label):
    label.set_text("")
