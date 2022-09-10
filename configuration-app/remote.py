""" Module is part of the Budgie Pi Configuration tool.
    This will handle all the associated services for the
    remote options.  Currently it will allow the installation,
    enabling and disabling of vnc, xrdp, ssh, and FindMyPi services.
"""

from ctypes.wintypes import PDWORD
import getpass
import socket
import subprocess
import psutil
import hint
import vncdialog
import apthelper
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk

VNC = 0
XRDP = 1
SSH = 2
FINDPI = 3


class Remote:
    """ Handle the installation, enabling and disabling of the various remote
        services: vnc, xrdp, ssh, and FindMyPi server. Remote options will be
        handled through Budgie Control Center when possible
    """
    SERVICES = ["/usr/lib/budgie-desktop/arm/budgie-vnc.sh",
                "/usr/lib/budgie-desktop/arm/budgie-xrdp.sh",
                "/usr/lib/budgie-desktop/arm/budgie-ssh.sh",
                "/usr/lib/budgie-desktop/arm/findmypiserver.py"]
    AUTOLOGIN = "/usr/lib/budgie-desktop/arm/budgie-autologin.sh"
    LIGHTDMCONF = "/etc/lightdm/lightdm.conf"

    def __init__(self, builder):
        """ set up the  GUI elements and check the status of the services """
        self.setup_gui(builder)
        self.refresh_ip()

        if self.run_findmypi:
            if not self.findmypi_server():
                self.start_findmypi()
            self.service_labels[FINDPI].set_text("FindMyPi is Enabled")
        else:
            self.service_labels[FINDPI].set_text("FindMyPi is Disabled")

        self.remote_hints = [hint.VNC_BUTTON, hint.XRDP_BUTTON, hint.SSH_BUTTON]
        for service in [VNC, XRDP, SSH]:
            self.run_remote(self.service_labels[service], self.SERVICES[service], 'status')
            if "abled" in self.service_labels[service].get_text():
                hint.add(self.service_buttons[service], self.app_statuslabel,
                         self.remote_hints[service])

    def setup_gui(self, builder):
        """ Set up the GUI elements """
        self.window = builder.get_object("ConfigWindow")
        self.spinner = builder.get_object("StatusSpinner")
        self.iplabel = builder.get_object("IPLabel")
        self.gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')
        self.locksetting = Gio.Settings.new('org.gnome.desktop.screensaver')
        self.run_findmypi = self.gsettings.get_boolean('enableserver')
        self.app_statuslabel = builder.get_object("AppStatusLabel")

        self.service_buttons = [builder.get_object("VNCButton"),
                                builder.get_object("XRDPButton"),
                                builder.get_object("SSHButton"),
                                builder.get_object("FindMyPiButton")]
        self.service_labels = [builder.get_object("VNCStatusLabel"),
                               builder.get_object("XRDPStatusLabel"),
                               builder.get_object("SSHStatusLabel"),
                               builder.get_object("FindMyPiStatusLabel")]
        connect = [self.vncbuttonclicked, self.xrdpbuttonclicked,
                   self.sshbuttonclicked, self.findmypibuttonclicked]
        initial_hints = [hint.VNC_NOT_INSTALLED, hint.XRDP_NOT_INSTALLED,
                         hint.SSH_NOT_INSTALLED, hint.FINDMYPI_SERVER]

        for index, button in enumerate(self.service_buttons):
            button.connect("clicked", connect[index])
            hint.add(button, self.app_statuslabel, initial_hints[index])

        self.autologincheck = builder.get_object("AutoLoginCheckButton")
        self.autologincheck.set_active(self.is_autologin())
        self.autologin_handler = self.autologincheck.connect("toggled", self.autologintoggled)
        tab = builder.get_object("RemoteTab")
        refresh_ip_button = builder.get_object("RefreshIPButton")
        hint.add(refresh_ip_button, self.app_statuslabel, hint.REFRESH_IP)
        hint.add(self.autologincheck, self.app_statuslabel, hint.AUTOLOGIN)
        hint.add(tab, self.app_statuslabel, hint.REMOTE_TAB)

    def run_remote(self, label, connection, param, root=False, alt_param=[]):
        """ run the remote service scripts to enable / disable / check status """
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

    def _pre_install(self, service):
        """ GUI elements to update before install starts """
        self.service_buttons[service].set_sensitive(False)
        self.service_labels[service].set_text("Installing - Please Wait")
        self.spinner.start()

    def _post_install(self, service):
        """ Update GUI and check service status after service is installed """
        self.run_remote(self.service_labels[service], self.SERVICES[service], 'status')
        if "abled" in self.service_labels[service].get_text():
            hint.add(self.service_buttons[service], self.app_statuslabel,
                     self.remote_hints[service])
        self.service_buttons[service].set_sensitive(True)
        self.spinner.stop()

    def xrdpbuttonclicked(self, button):
        """ Enable / Disable xrdp or install xrdp if needed"""
        def enablegui(): return self._post_install(XRDP)
        if 'Enabled' in self.service_labels[XRDP].get_text():
            self.run_remote(self.service_labels[XRDP], self.SERVICES[XRDP], 'disable')
        elif 'Not Installed' in self.service_labels[XRDP].get_text():
            self._pre_install(XRDP)
            # modal should prevent most issues such as closing the app during install
            apt = apthelper.AptHelper(transient_for=self.window, modal=True)
            apt.install(packages=['xrdp'], success_callback=enablegui,
                        failed_callback=enablegui, cancelled_callback=enablegui)
        else:
            self.run_remote(self.service_labels[XRDP], self.SERVICES[XRDP], 'enable')

    def sshbuttonclicked(self, button):
        """ Toggle the SSH service """
        def enablegui(): return self._post_install(SSH)
        if 'Not Installed' not in self.service_labels[SSH].get_text():
            self.open_sharing()
            self.run_remote(self.service_labels[SSH], self.SERVICES[SSH], 'status')
        else:
            self._pre_install(SSH)
            # modal should prevent most issues such as closing the app during install
            apt = apthelper.AptHelper(transient_for=self.window, modal=True)
            apt.install(packages=['openssh-server'], success_callback=enablegui,
                        failed_callback=enablegui, cancelled_callback=enablegui)

    def findmypibuttonclicked(self, button):
        """ Toggle the FindMyPi server """
        if self.findmypi_server():
            self.findmypi_server(kill=True)
            self.gsettings.set_boolean('enableserver', False)
            self.service_labels[FINDPI].set_text("FindMyPi is Disabled")
        else:
            self.start_findmypi()
            self.gsettings.set_boolean('enableserver', True)
            self.service_labels[FINDPI].set_text("FindMyPi is Enabled")

    @staticmethod
    def open_sharing():
        """ Open Remote Sharing settings via Control Center if available """
        control_center = "gnome-control-center"
        if GLib.find_program_in_path("budgie-control-center") is not None:
            control_center = "budgie-control-center"
        try:
            subprocess.run([control_center, 'sharing'])
        except subprocess.CalledProcessError:
            pass

    def activate_vnc(self, extra_args=[], disable=False):
        """ Toggle the VNC service """
        if disable:
            self.run_remote(self.service_labels[VNC], self.SERVICES[VNC],
                            'disable')
        else:
            self.run_remote(self.service_labels[VNC], self.SERVICES[VNC],
                            'setup', alt_param=extra_args)
        self.run_remote(self.service_labels[VNC], self.SERVICES[VNC], 'status')
        return False

    def vncbuttonclicked(self, button):
        """ Install VNC if not present, or set up the VNC service if it is """
        if "Not Installed" in self.service_labels[VNC].get_text():
            def enablegui(): return self._post_install(VNC)
            self._pre_install(VNC)
            # modal should prevent most issues such as closing the app during install
            apt = apthelper.AptHelper(transient_for=self.window, modal=True)
            apt.install(packages=['x11vnc'], success_callback=enablegui,
                        failed_callback=enablegui, cancelled_callback=enablegui)
            return
        stopservice = 'Enabled' in self.service_labels[VNC].get_text()
        self.service_labels[VNC].set_text("Please wait...")
        if stopservice:
            # Sometimes, x11vnc takes a while to stop, making app seem unresponsive
            # Timeout allows the "please wait" message to appear
            GLib.timeout_add(10, self.activate_vnc, [], True)
        else:
            vnc_args = []
            pwdialog = vncdialog.VncDialog()
            response = pwdialog.run()
            if response == Gtk.ResponseType.OK:
                password = pwdialog.get_result()
                vnc_args.append(password)
                if pwdialog.get_viewonly():
                    vnc_args.append("viewonly")
                else:
                    vnc_args.append("control")
                if pwdialog.get_localhost():
                    subnet = "127.0.0.1"
                    vnc_args.append(subnet)
                elif pwdialog.get_restrict():
                    # get the ip (needed to restrict VNC to local subnet)
                    subnet = ".".join(self.get_ip().split(".", 3)[:-1]) + "."
                    vnc_args.append(subnet)
                pwdialog.destroy()
                GLib.idle_add(self.activate_vnc, vnc_args, False)
            else:
                self.run_remote(self.service_labels[VNC], self.SERVICES[VNC], 'status')
                pwdialog.destroy()

    def autologintoggled(self, button):
        """ Enable or disable the OS login """
        should_enable = button.get_active()
        if should_enable:
            user = getpass.getuser()
        else:
            user = ''
        if self.get_current_autologin() != user:
            args = ['pkexec', self.AUTOLOGIN, user]
            try:
                subprocess.check_output(args,
                                        stderr=subprocess.STDOUT).decode("utf-8").strip('\'\n')
            except subprocess.CalledProcessError as e:
                print(e.output.decode("utf-8"))
                self.autologincheck.handler_block(self.autologin_handler)
                self.autologincheck.set_active(not should_enable)
                self.autologincheck.handler_unblock(self.autologin_handler)
                # pkexec wasn't successful - return without changing screen lock
                return
        self.locksetting.set_boolean('lock-enabled', not should_enable)

    def get_current_autologin(self):
        """ return the current user set up to autologin """
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
        """ return True if screen lock is off and autologin is current user """
        if (self.locksetting.get_boolean('lock-enabled') or
                self.get_current_autologin() != getpass.getuser()):
            return False
        return True

    @staticmethod
    def get_ip():
        """ Return the current IP address """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            sock.connect(('10.255.255.255', 1))
            ip_addr = sock.getsockname()[0]
        except Exception:
            ip_addr = '127.0.0.1'
        finally:
            sock.close()
        return ip_addr

    def refresh_ip(self):
        """ Update the GUI to show the current IP address """
        self.iplabel.set_text(self.get_ip())

    def start_findmypi(self):
        """ Starts the FindMyPi server """
        try:
            subprocess.Popen(['python3', self.SERVICES[FINDPI]])
        except OSError as e:
            print("Error:", e)

    @staticmethod
    def findmypi_server(kill=False):
        """ Return True if server is running, also will kill server if kill=True """
        for proc in psutil.process_iter():
            if (len(proc.cmdline()) > 1 and "python" in proc.cmdline()[0]
                    and "findmypiserver" in proc.cmdline()[1]):
                if kill:
                    proc.terminate()
                    return False
                return True
        return False
