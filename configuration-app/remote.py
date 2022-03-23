import socket
import subprocess
import psutil
import gi
import getpass
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio
import hint


class Remote:

    XRDP = "/usr/lib/budgie-desktop/arm/budgie-xrdp.sh"
    SSH = "/usr/lib/budgie-desktop/arm/budgie-ssh.sh"
    FINDPI = "/usr/lib/budgie-desktop/arm/findmypiserver.py"
    AUTOLOGIN = "/usr/lib/budgie-desktop/arm/budgie-autologin.sh"
    LIGHTDMCONF = "/etc/lightdm/lightdm.conf"

    def __init__(self, builder, device):
        self.iplabel = builder.get_object("IPLabel")
        self.refresh_ip()
        self.gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')
        self.locksetting = Gio.Settings.new('org.gnome.desktop.screensaver')
        self.run_findmypi = self.gsettings.get_boolean('enableserver')
        app_statuslabel = builder.get_object("AppStatusLabel")

        if GLib.find_program_in_path("pipewire") == None:
            self.found_grd = False
        else:
            self.found_grd = True

        self.vncbutton = builder.get_object("VNCButton")
        self.vncbutton.connect('clicked', self.vncbuttonclicked)
        # Temporarily disabled
        # self.vncbutton.set_visible(self.found_grd)
        self.vncbutton.set_visible(False)

        self.xrdpbutton = builder.get_object("XRDPButton")
        self.xrdpbutton.connect('clicked', self.xrdpbuttonclicked)

        self.xrdpstatuslabel = builder.get_object("XRDPStatusLabel")
        self.sshstatuslabel = builder.get_object("SSHStatusLabel")
        self.findmypistatuslabel = builder.get_object("FindMyPiStatusLabel")

        self.sshbutton = builder.get_object("SSHButton")
        self.sshbutton.connect('clicked', self.sshbuttonclicked)

        self.autologincheck = builder.get_object("AutoLoginCheckButton")
        self.autologincheck.set_active(self.is_autologin())
        self.autologin_handler = self.autologincheck.connect("toggled", self.autologintoggled)

        self.findmypibutton = builder.get_object("FindMyPiButton")
        self.findmypibutton.connect('clicked', self.findmypibuttonclicked)

        tab = builder.get_object("RemoteTab")
        refresh_ip_button = builder.get_object("RefreshIPButton")

        hint.add(refresh_ip_button, app_statuslabel, hint.REFRESH_IP)
        hint.add(self.autologincheck, app_statuslabel, hint.AUTOLOGIN)
        hint.add(self.findmypibutton, app_statuslabel, hint.FINDMYPI_SERVER)
        hint.add(self.sshbutton, app_statuslabel, hint.SSH_BUTTON)
        hint.add(self.xrdpbutton, app_statuslabel, hint.XRDP_BUTTON)
        hint.add(self.vncbutton, app_statuslabel, hint.VNC_BUTTON)
        hint.add(tab, app_statuslabel, hint.REMOTE_TAB)

        if self.run_findmypi:
            if not self.findmypi_server():
                self.start_findmypi()
            self.findmypistatuslabel.set_text("Server is active")
        else:
            self.findmypistatuslabel.set_text("Server is inactive")

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

    def findmypibuttonclicked(self, *args):
        if self.findmypi_server():
            self.findmypi_server(kill=True)
            self.gsettings.set_boolean('enableserver', False)
            self.findmypistatuslabel.set_text("Server is inactive")
        else:
            self.start_findmypi()
            self.gsettings.set_boolean('enableserver', True)
            self.findmypistatuslabel.set_text("Server is active")

    def open_sharing(self):
        try:
            subprocess.run(['budgie-control-center', 'sharing'])
        except subprocess.CalledProcessError:
            pass

    def vncbuttonclicked(self, *args):
        self.open_sharing()

    def autologintoggled(self, button):
        should_enable = button.get_active()
        if should_enable:
            user = getpass.getuser()
        else:
            user = ''
        if self.get_current_autologin() != user:
            args = ['pkexec', self.AUTOLOGIN, user]
            try:
                output = subprocess.check_output(args,
                        stderr=subprocess.STDOUT).decode("utf-8").strip('\'\n')
            except subprocess.CalledProcessError as e:
                output = e.output.decode("utf-8")
                self.autologincheck.handler_block(self.autologin_handler)
                self.autologincheck.set_active(not should_enable)
                self.autologincheck.handler_unblock(self.autologin_handler)
                #pkexec wasn't successful - return without changing screen lock
                return
        self.locksetting.set_boolean('lock-enabled', not should_enable)

    def get_current_autologin(self):
        # Return the autologin user from lightdm.conf, if any
        try:
            with open(self.LIGHTDMCONF, 'r') as lightdmconf:
                lines = lightdmconf.readlines()
                for line in lines:
                    current = line.strip().split('=')
                    if len(current) == 2 and current[0] == 'autologin-user':
                        return current[1]
        except EnvironmentError:
            pass
        return ''

    def is_autologin(self):
        # True only if screen lock is off and autologin is current user
        if (self.locksetting.get_boolean('lock-enabled') or
                self.get_current_autologin() != getpass.getuser()):
            return False
        else:
            return True

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

    def start_findmypi(self):
        try:
            subprocess.Popen(['python3', self.FINDPI])
        except OSError as e:
            print("Error:", e)

    def findmypi_server(self, kill=False):
        # Return True if server is running, also will kill server if kill=True
        for proc in psutil.process_iter():
            if (len(proc.cmdline()) > 1 and "python" in proc.cmdline()[0]
                                   and "findmypiserver" in proc.cmdline()[1]):
                if kill:
                    proc.terminate()
                else:
                    return True
        return False
