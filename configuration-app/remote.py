import pwd
import socket
import subprocess
import psutil
import gi
import getpass
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
import hint
import vncdialog
import apthelper

class Remote:

    XRDP = "/usr/lib/budgie-desktop/arm/budgie-xrdp.sh"
    SSH = "/usr/lib/budgie-desktop/arm/budgie-ssh.sh"
    FINDPI = "/usr/lib/budgie-desktop/arm/findmypiserver.py"
    AUTOLOGIN = "/usr/lib/budgie-desktop/arm/budgie-autologin.sh"
    LIGHTDMCONF = "/etc/lightdm/lightdm.conf"
    VNC = "/usr/lib/budgie-desktop/arm/budgie-vnc.sh"

    def __init__(self, builder, device):

        self.window = builder.get_object("ConfigWindow")
        self.spinner = builder.get_object("StatusSpinner")

        self.iplabel = builder.get_object("IPLabel")
        self.refresh_ip()
        self.gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')
        self.locksetting = Gio.Settings.new('org.gnome.desktop.screensaver')
        self.run_findmypi = self.gsettings.get_boolean('enableserver')
        self.app_statuslabel = builder.get_object("AppStatusLabel")

        self.vncbutton = builder.get_object("VNCButton")
        self.vncbutton.connect('clicked', self.vncbuttonclicked)

        self.xrdpbutton = builder.get_object("XRDPButton")
        self.xrdpbutton.connect('clicked', self.xrdpbuttonclicked)

        self.vncstatuslabel = builder.get_object("VNCStatusLabel")
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

        hint.add(refresh_ip_button, self.app_statuslabel, hint.REFRESH_IP)
        hint.add(self.autologincheck, self.app_statuslabel, hint.AUTOLOGIN)
        hint.add(self.findmypibutton, self.app_statuslabel, hint.FINDMYPI_SERVER)
        hint.add(self.sshbutton, self.app_statuslabel, hint.SSH_NOT_INSTALLED)
        hint.add(self.xrdpbutton, self.app_statuslabel, hint.XRDP_BUTTON)
        hint.add(self.vncbutton, self.app_statuslabel, hint.VNC_BUTTON)
        hint.add(tab, self.app_statuslabel, hint.REMOTE_TAB)

        if self.run_findmypi:
            if not self.findmypi_server():
                self.start_findmypi()
            self.findmypistatuslabel.set_text("Server is active")
        else:
            self.findmypistatuslabel.set_text("Server is inactive")

        self.run_remote(self.xrdpstatuslabel, self.XRDP, 'status')
        self.run_remote(self.sshstatuslabel, self.SSH, 'status')
        self.run_remote(self.vncstatuslabel, self.VNC, 'status')

        if "is installed" in self.sshstatuslabel.get_text():
            hint.add(self.sshbutton, self.app_statuslabel, hint.SSH_BUTTON)


    def run_remote(self, label, connection, param, root=False, alt_param = []):

        if root:
            args = ['pkexec', connection, param]
        else:
            args = [connection, param]

        if alt_param != []:
            # VNC setup needs extra params, probably rework this in the future
            args += (alt_param)

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
        def enablegui():
            self.run_remote(self.sshstatuslabel, self.SSH, 'status')
            if "is installed" in self.sshstatuslabel.get_text():
                hint.add(self.sshbutton, self.app_statuslabel, hint.SSH_BUTTON)
            self.sshbutton.set_sensitive(True)
            self.spinner.stop()

        if 'ssh is installed' in self.sshstatuslabel.get_text():
            self.open_sharing()
            self.run_remote(self.sshstatuslabel, self.SSH, 'status')

        else:
            self.spinner.start()
            self.sshbutton.set_sensitive(False)
            self.sshstatuslabel.set_text("Installing\nPlease Wait...")
            # modal should prevent most issues such as closing the app during install
            apt = apthelper.AptHelper(transient_for=self.window, modal=True)
            apt.install(packages=['openssh-server'], success_callback=enablegui,
                                                     failed_callback=enablegui,
                                                     cancelled_callback=enablegui)

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

    def activate_vnc(self, extra_args=[], disable=False):
        if disable:
            self.run_remote(self.vncstatuslabel, self.VNC, 'disable', root=True)
        else:
            self.run_remote(self.vncstatuslabel, self.VNC, 'setup', root=True, alt_param=extra_args)
        self.run_remote(self.vncstatuslabel,self.VNC,'status')
        return False

    def vncbuttonclicked(self, *args):
        stopservice = 'vnc service is active' in self.vncstatuslabel.get_text()
        self.vncstatuslabel.set_text("Please wait...")
        if stopservice:
            # Sometimes, x11vnc takes a while to stop, making app seem unresponsive
            # Timeout allows the "please wait" message to appear
            GLib.timeout_add(10,self.activate_vnc, [], True)
        else:
            # get the ip (needed to restrict VNC to local subnet)
            subnet =".".join(self.get_ip().split(".", 3)[:-1]) + "."
            pwdialog = vncdialog.VncDialog()
            response = pwdialog.run()
            if response == Gtk.ResponseType.OK:
                password = pwdialog.get_result()
                pwdialog.destroy()
                GLib.idle_add(self.activate_vnc, [password, subnet], False)
            else:
                self.run_remote(self.vncstatuslabel, self.VNC, 'status')
                pwdialog.destroy()

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
