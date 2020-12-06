import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import dbus
import subprocess
import time
from remote import Remote
from overclock import Overclock
from layout import DefaultLayout, CompactLayout

class Handler:
    def on_ConfigWindow_destroy(self, *args):
        Gtk.main_quit()

    def on_CompactButton_clicked(self):
        compactlayout.apply()

    def on_DefaultButton_clicked(self):
        defaultlayout.apply()
        
    def on_RefreshIP_Clicked(self):
        iplabel.set_text(Remote.get_ip())

builder = Gtk.Builder()
builder.add_from_file("config.ui")
builder.connect_signals(Handler)

compactlayout = CompactLayout()
defaultlayout = DefaultLayout()
width, height, xoffset, yoffset = compactlayout.getres()

window = builder.get_object("ConfigWindow")

window.show_all()
logoutloginlabel = builder.get_object("LogoutLoginLabel")
logoutloginlabel.set_visible(False)

iplabel = builder.get_object("IPLabel")
Handler.on_RefreshIP_Clicked(None)

overclockgrid = builder.get_object("OverclockGrid")
cpuTempLabel = builder.get_object("cpuTempLabel")

if Overclock.is_raspi():
    GLib.timeout_add_seconds(1,Overclock.temp_monitor)
else:
    overclockgrid.set_visible(False)

if height <= 768:
    compactlayout.ask_to_reset()

Gtk.main()
