# Budgie ARM Configuration Tool

Install:

create folder /usr/lib/budgie-desktop/arm
copy the file reset.sh into this folder

copy the file ubuntubudgiecompact.layout to /usr/share/budgie-desktop/layouts

run the app:

    python3 main.py

To Do:

- [X] split test.py into python modules - one module per tab
- [ ] Implement start on logon
- [ ] when opening, navigate to last tab that was opened before closing
- [X] Display users current IP address - probably https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib/28950776#28950776
- [X] Overclock: Display CPU temperature (update once a second) - Sam's temperature code
- [ ] Overclock: Overclocking CPU choice - pibootctl
- [ ] Overclock: Hide overclock tab if not running on a raspi: https://github.com/wimpysworld/desktopify/blob/50b72f96ea921618cf30b85b6ba147fc929a85cb/desktopify#L211

Nice to have:

- [ ] Enable VNC Server: start/stop VNC - dunno how
- [ ] "FindMyPi" - setup a UDP server - something like https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python - on connecting return the IP address of the PI
- [ ] "FindMyPi" - client version of app with a big "FindMyPi" that displays the IP address of the PI on the network
- [ ] Enable SSH: install openssh-server if not installed - use packagekit python module at a guess
- [ ] Enable SSH: start/stop SSH - probably https://linuxize.com/post/how-to-enable-ssh-on-ubuntu-18-04/
