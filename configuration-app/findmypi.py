import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Gio
from findmypiclient import FindMyPiTreeView
import getpass
import re
import time
import hint
import apthelper


class FindMyPi:

    def __init__(self, builder):

        # If method='server', it looks for findmypiserver.py running on remote
        # If method='mac', it will look via mac (needs nmap installed)
        self.findpi_treeview = FindMyPiTreeView()

        self.replace_gui(builder)
        self.findpi_statuslabel = builder.get_object("PiStatusLabel")
        self.app_statuslabel = builder.get_object("AppStatusLabel")
        self.refresh_button = builder.get_object("PiRefreshButton")
        self.copyip_button = builder.get_object("PiCopyIpButton")
        self.ssh_button = builder.get_object("PiSSHButton")
        self.nmap_button = builder.get_object("NmapButton")
        self.sshuser_entry = builder.get_object("SSHUserEntry")
        self.spinner = builder.get_object("StatusSpinner")
        self.gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')

        if self._has_nmap() and self.gsettings.get_boolean('nmapscan'):
            if self._nmap_warn():
                self.findpi_treeview.set_method('mac')
                self.nmap_button.set_label("Disable nmap")
            else:
                self.gsettings.set_boolean('nmapscan', False)
                self.findpi_treeview.set_method('server')
                self.nmap_button.set_label("Enable nmap")
        else:
            self.findpi_treeview.set_method('server')
            self.nmap_button.set_label("Enable nmap")

        self.nmap_button.connect("clicked", self.on_nmap_button_clicked)
        hint.add(self.nmap_button, self.app_statuslabel, hint.NMAP_BUTTON)
        self.refresh_button.connect("clicked",  self.on_refresh_clicked)
        hint.add(self.refresh_button, self.app_statuslabel, hint.REFRESH_BUTTON)
        self.copyip_button.connect("clicked", self.on_copyip_clicked)
        hint.add(self.copyip_button, self.app_statuslabel, hint.COPYIP_BUTTON)
        self.ssh_button.connect("clicked", self.on_ssh_clicked)
        hint.add(self.ssh_button, self.app_statuslabel, hint.SSH_BUTTON)

        self.sshuser_entry.set_text(getpass.getuser())
        hint.add(self.sshuser_entry, self.app_statuslabel, hint.SSH_ENTRY)
        self.findpi_treeview.start()

    def replace_gui(self, builder):
        main_grid = builder.get_object("ConfigGrid")
        findpi_grid = builder.get_object("FindMyPiGrid")
        notebook = builder.get_object("ConfigNotebook")
        findpi_scrolledwindow = builder.get_object("FindMyPiWindow")
        findpi_scrolledwindow.set_size_request(480,-1)
        main_grid.remove(notebook)
        findpi_scrolledwindow.add(self.findpi_treeview)
        main_grid.attach(findpi_grid, 0, 0, 2, 1)
        findpi_grid.show_all()

    def on_refresh_clicked(self, button):
        # if checking via arp, don't do nmap if it's been done in last 30 secs
        if not self.findpi_treeview.use_arp:
            self.findpi_treeview.refresh_list()
        else:
            if (time.time() - self.findpi_treeview.findpi.last_scan) > 20:
                self.findpi_treeview.findpi.last_scan = 0
            self.findpi_treeview.refresh_list()

    def on_copyip_clicked(self, button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        ip = self.findpi_treeview.get_value_at_col(0)
        if ip != "" and ip != "Searching":
            self.change_label("{} copied!".format(ip))
            clipboard.set_text(ip, -1)
            GLib.timeout_add_seconds(3, self.change_label, "")

    def on_nmap_button_clicked(self, button):
        if not self._has_nmap():
            self.spinner.start()
            button.set_sensitive(False)
            if self._ask_install_nmap():
                self.change_label("Installing...")
                self._install_nmap()
            else:
                button.set_sensitive(True)
                self.spinner.stop()
        elif self.findpi_treeview.use_arp:
            button.set_label("Enable nmap")
            self.findpi_treeview.use_arp = False
            self.findpi_treeview.refresh_list()
            self.gsettings.set_boolean('nmapscan', False)
        else:
            self.findpi_treeview.use_arp = True
            button.set_label("Disable nmap")
            self.findpi_treeview.refresh_list()
            self.gsettings.set_boolean('nmapscan', True)

    def on_ssh_clicked(self, button):
        ip = self.findpi_treeview.get_value_at_col(0)
        if ip == "" or ip == "Searching":
            return
        command = ip
        username = self.sshuser_entry.get_text().strip()
        if username != "":
            sshuser = re.sub('[^A-Za-z0-9_$-]', '', username)
            if sshuser != username:
                # Don't spawn ssh if there are bad characters in username
                return
            command = sshuser + "@" + ip
        preferred_terminal = GLib.find_program_in_path("x-terminal-emulator")
        try:
            if preferred_terminal is not None:
                command_line = " ".join([preferred_terminal,"-e","ssh",command])
                ssh_app = Gio.AppInfo.create_from_commandline (command_line, preferred_terminal,
                                                            Gio.AppInfoCreateFlags.NONE)
            else:
                ssh_app = Gio.AppInfo.create_from_commandline ("ssh " + command, "ssh",
                                                            Gio.AppInfoCreateFlags.NEEDS_TERMINAL)
            ssh_app.launch(None, None)
        except Exception as e:
            print(e.message)

    def change_label(self, new_text):
        self.findpi_statuslabel.set_text(new_text)
        return False

    def _has_nmap(self):
        return GLib.find_program_in_path('nmap')

    def _nmap_warn(self):
        if self.gsettings.get_boolean('disablewarning'):
            return True
        nmap_dialog = Gtk.MessageDialog(None, flags=0,
                                        message_type=Gtk.MessageType.WARNING,
                                        buttons=Gtk.ButtonsType.OK_CANCEL,
                                        text="Warning - nmap mode!")
        nmap_dialog.format_secondary_text(
              "FindMyPi will use nmap to search for PIs. Please check that "
            + "there are no legality issues with scanning this network. If "
            + "you are unsure, please select Cancel to scan by UDP server." )
        warn_checkbutton = Gtk.CheckButton(" Don't show this again")
        warn_checkbutton.show()
        nmap_dialog.action_area.pack_end(warn_checkbutton, True, True, 25)
        nmap_dialog.action_area.set_homogeneous(False)
        response = nmap_dialog.run()
        nmap_dialog.destroy()
        self.gsettings.set_boolean('disablewarning',
                                    warn_checkbutton.get_active())
        if response == Gtk.ResponseType.OK:
            return True
        else:
            return False

    def _ask_install_nmap(self):
        nmap_dialog = Gtk.MessageDialog(None, flags=0,
                                        message_type=Gtk.MessageType.WARNING,
                                        buttons=Gtk.ButtonsType.YES_NO,
                                        text="Install Nmap?")
        nmap_dialog.format_secondary_text(
              "Nmap not installed.  Before installing nmap, please ensure "
            + "there are no legality issues with installing and using nmap "
            + "on this network.  If you are unsure, please select NO.\n"
            + "Install nmap?")
        response = nmap_dialog.run()
        nmap_dialog.destroy()
        if response == Gtk.ResponseType.NO:
            return False
        else:
            return True

    def _install_nmap(self):

        def reenable():
            self.nmap_button.set_sensitive(True)
            self.change_label("")
            self.spinner.stop()

        def postinstall():
            if self._has_nmap():  #  just to be 100% sure
                self.nmap_button.set_label("Disable nmap")
                self.findpi_treeview.use_arp = True
                self.gsettings.set_boolean('nmapscan', True)
                self.findpi_treeview.refresh_list()
            reenable()

        def failedinstall():
            dialog = Gtk.MessageDialog(None, flags=0,
                                       message_type=Gtk.MessageType.ERROR,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Could not install nmap")
            dialog.run()
            dialog.destroy()
            reenable()

        self.change_label("Installing...")
        apt = apthelper.AptHelper()
        apt.install(['nmap'], success_callback=postinstall,
                              failed_callback=failedinstall,
                              cancelled_callback=reenable)
