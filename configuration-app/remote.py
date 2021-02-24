import socket
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib



class Remote:

    XRDP = "/usr/lib/budgie-desktop/arm/budgie-xrdp.sh"
    SSH = "/usr/lib/budgie-desktop/arm/budgie-ssh.sh"

    def __init__(self,builder):
        self.iplabel = builder.get_object("IPLabel")
        self.refresh_ip()

        if GLib.find_program_in_path("pipewire") == None:
            self.found_grd = False
        else:
            self.found_grd = True

        self.vncbutton = builder.get_object("VNCButton")
        self.vncbutton.connect('clicked', self.vncbuttonclicked)
        self.vncbutton.set_visible(self.found_grd)

        self.xrdpbutton = builder.get_object("XRDPButton")
        self.xrdpbutton.connect('clicked', self.xrdpbuttonclicked)

        self.xrdpstatuslabel = builder.get_object("XRDPStatusLabel")
        self.sshstatuslabel = builder.get_object("SSHStatusLabel")

        self.sshbutton = builder.get_object("SSHButton")
        self.sshbutton.connect('clicked', self.sshbuttonclicked)

        self.run_remote(self.xrdpstatuslabel, self.XRDP, 'status')
        if not self.found_grd:
            self.run_remote(self.sshstatuslabel, self.SSH, 'status')

    def run_remote(self, label, connection, param, root=False):

        if root:
            args = ['pkexec', connection, param]
        else:
            args = [connection, param]

        try:
            output = subprocess.check_output(args,
                stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")

        if 'root' in output:
            self.run_remote(label, connection, param, root=True)
            self.run_remote(label, connection, 'status')
        else:
            label.set_text(output[0:50].rstrip('\n'))

    def xrdpbuttonclicked(self, *args):
        if 'service is ok' in self.xrdpstatuslabel.get_text():
            self.run_remote(self.xrdpstatuslabel, self.XRDP, 'disable')
        else:
            self.run_remote(self.xrdpstatuslabel, self.XRDP, 'enable')

    def sshbuttonclicked(self, *args):
        if self.found_grd:
            # with gnome-remote-desktop ssh is provided
            self.open_sharing()
            return

        if 'service is active' in self.sshstatuslabel.get_text():
            self.run_remote(self.sshstatuslabel, self.SSH, 'disable')
        else:
            self.run_remote(self.sshstatuslabel, self.SSH, 'enable')

    def open_sharing(self):
        try:
            subprocess.run(['gnome-control-center', 'sharing'])
        except subprocess.CalledProcessError:
            pass

    def vncbuttonclicked(self, *args):
        self.open_sharing()

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def refresh_ip(self):
        self.iplabel.set_text(self.get_ip())
