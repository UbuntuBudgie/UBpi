# Budgie ARM Configuration Tool

## Install:

    sudo apt install libglib2.0-dev-bin
    git clone https://github.com/UbuntuBudgie/UBpi
    cd UBpi/configuration-app
    mkdir build && cd build
    meson --prefix=/usr --libdir=/usr/lib
    sudo ninja install

If installing, it may be necessary aftaer install to run:

    sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

## To Do:

- [X] Hide ssh/vnc  checkboxes until implementation
- [ ] Need an icon for the application
- [X] split test.py into python modules - one module per tab
- [X] Implement start on logon
- [X] when opening, navigate to last tab that was opened before closing
- [X] Display users current IP address - probably https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib/28950776#28950776
- [X] Overclock: Display CPU temperature (update once a second) - Sam's temperature code
- [X] Overclock: Overclocking CPU choice - pibootctl
- [X] Overclock: Hide overclock tab if not running on a raspi: https://github.com/wimpysworld/desktopify/blob/50b72f96ea921618cf30b85b6ba147fc929a85cb/desktopify#L211

## Nice to have:

- [ ] option for the compact/mini layouts to enable xrandr pan and scrolling for lower screen devices such as the raspi touch screen
- [X] Enable VNC Server: start/stop VNC - dunno how
- [X] "FindMyPi" - setup a UDP server - something like https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python - on connecting return the IP address of the PI
- [X] "FindMyPi" - client version of app with a big "FindMyPi" that displays the IP address of the PI on the network
- [X] Enable SSH: install openssh-server if not installed - use packagekit python module at a guess
- [X] Enable SSH: start/stop SSH - probably https://linuxize.com/post/how-to-enable-ssh-on-ubuntu-18-04/
- [X] Headless mode: one click method to switch to auto logon, turn off screensaver etc.
- [X] Setup XRDP: RDP is superior to vnc so a one click method along these lines would be useful https://froth-and-java.dev/posts/ubuntu-budgie-and-xrdp
- [ ] Look at touch-screen long right click methods https://github.com/bareboat-necessities/evdev-right-click-emulation https://github.com/bareboat-necessities/my-bareboat/blob/master/right-click-emu/right-click-emu.sh
