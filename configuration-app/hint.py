#General
AUTOSTART = "Enable or disable autostart of the configuration tool"

#Layouts Tab
LAYOUTS_TAB = "Configure different display options for smaller screens"
STANDARD_RES = "Recommended for screens with\nvertical resolutions of 900 and above"
COMPACT_RES = "Recommended for small screens with\nvertical resolutions of at least 768"
MINI_RES = "Recommended for small screens with\nvertical resolutions of less than 768"
APPLY_LAYOUT = "Apply the new layout.\nLogout/Login required to complete"

#Overclock Tab
OVERCLOCK_TAB = "Configure clock speed and view CPU temperature"
CPU_TEMP = "Current CPU temperature. The Pi will throttle at temperatures around 80°C. Overclocking may affect the throttle temp."
CPU_SPEEDS = "Higher speeds will increase performance, but may increase heat or cause instability. Pi400 cannot be set below 1.8GHz"
SPEED_BUTTON = "Apply the new clock speed.\nThe new speed will take effect after reboots"
NO_CONFIGTXT = "File '/boot/firmware/config.txt' not found.\nOverclock disabled - Is this a valid Pi?"

#Remote Tab
REMOTE_TAB = "Options to configure remote access to this device"
REFRESH_IP = "Updates the IP if you have changed connection\nmethod, or connected to a new network."
FINDMYPI_SERVER = "Enable FindMyPi UDP server on app startup. This is not needed when using nmap on the client"
AUTOLOGIN = "Enable automatic login, and disable the lock screen to prevent issues accessing this device through VNC"
XRDP_BUTTON = "Enable / disable Ubuntu Budgie's XRDP access. This should not be used when Gnome's RDP is enabled."
XRDP_NOT_INSTALLED = "Ubuntu Budgie provides an alternative xrdp option.\nThis will install the xrdp package."
SSH_BUTTON = "Enable SSH access to this device, using Budgie Remote Desktop settings."
SSH_NOT_INSTALLED ="SSH access is not currently available. This will install OpenSSH to enable this option in Budgie Desktop Settings."
VNC_BUTTON = "Enable VNC access to this device, VNC allows screen sharing. Enabling / Disabling VNC may take a minute to complete."

#Display Tab
DISPLAY_TAB = "Configure Video Modes and Video Memory"
VIDEO_MODE = "KMS mode is recommended for attached displays. FKMS is recommended for remote access. Legacy is non-accelerated."
GPU_MEMORY = "Select the amout of memory to reserve for video usage. Too large a value may hurt performance if it is not needed."
UPDATE_VIDEO = "Apply the selected video mode\nReboot required for changes to take effect"
UPDATE_MEMORY = "Apply the selected memory setting\nReboot required for changes to take effect"
NO_PIBOOTCTL = "Unable to make changes to the Display options.\nThis is not a Pi, or pibootctl may not be installed."

#Findmypi
NMAP_BUTTON = "When enabled, nmap is used to scan the network for Pis.\nIf disabled, it scans for Pis running the FindMyPi server."
REFRESH_BUTTON = "Rescan the network for Raspberry Pis"
COPYIP_BUTTON = "Copy the currently selected IP address to the clipboard"

def add(widget, label, status):
    widget.connect("enter-notify-event", set_label, label, status)
    widget.connect("leave-notify-event", clear_label, label)

def set_label(widget, event, label, status):
    label.set_text(status)

def clear_label(widget, event, label):
    label.set_text("")
