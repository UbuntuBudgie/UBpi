import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from findmypiclient import FindMyPiTreeView


class FindMyPi:

    def __init__(self, builder):

        # If method='server', it looks for findmypiserver.py running on remote
        # If method='mac', it will look via mac (needs arp and nmap installed)
        self.findpi_treeview = FindMyPiTreeView()
        if self._has_nmap():
            if self._nmap_warn():
                self.findpi_treeview.set_method('mac')
            else:
                self.findpi_treeview.set_method('server')
        else:
            self.findpi_treeview.set_method('server')

        self.replace_gui(builder)

        self.findpi_statuslabel = builder.get_object("PiStatusLabel")
        self.refresh_button = builder.get_object("PiRefreshButton")
        self.copyip_button = builder.get_object("PiCopyIpButton")
        self.refresh_button.connect("clicked",  self.on_refresh_clicked)
        self.copyip_button.connect("clicked", self.on_copyip_clicked)

        self.findpi_treeview.start()

    def replace_gui(self, builder):
        main_grid = builder.get_object("ConfigGrid")
        findpi_grid = builder.get_object("FindMyPiGrid")
        notebook = builder.get_object("ConfigNotebook")
        findpi_scrolledwindow = builder.get_object("FindMyPiWindow")
        main_grid.remove(notebook)
        findpi_scrolledwindow.add(self.findpi_treeview)
        main_grid.attach(findpi_grid, 0, 0, 2, 1)
        findpi_grid.show_all()

    def on_refresh_clicked(self, button):
        self.findpi_treeview.refresh_list()

    def on_copyip_clicked(self, button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        ip = self.findpi_treeview.get_value_at_col(0)
        if ip != "" and ip != "Searching":
            self.change_label("{} copied!".format(ip))
            clipboard.set_text(ip, -1)
            GLib.timeout_add_seconds(3, self.change_label, "")

    def change_label(self, new_text):
        self.findpi_statuslabel.set_text(new_text)
        return False

    def _has_nmap(self):
        return GLib.find_program_in_path('nmap')

    def _nmap_warn(self):
        nmap_dialog = Gtk.MessageDialog(None, flags=0,
                                        message_type=Gtk.MessageType.WARNING,
                                        buttons=Gtk.ButtonsType.OK_CANCEL,
                                        text="Warning - nmap mode!")
        nmap_dialog.format_secondary_text(
              "FindMyPi will use nmap to search for PIs. Please check that "
            + "there are no legality issues with scanning this network. If "
            + "you are unsure, please select Cancel to scan by UDP server." )
        response = nmap_dialog.run()
        nmap_dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        else:
            return False
