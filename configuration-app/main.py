import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import dbus
import subprocess
import time
from remote import Remote
from overclock import Overclock
from layout import Layout

class Handler:
    def on_ConfigWindow_destroy(self, *args):
        Gtk.main_quit()

    def on_MiniRadioButton_toggled(self):
        if miniradiobutton.get_active():
            layoutstyle.apply(Layout.MINI)

    def on_CompactRadioButton_toggled(self):
        if compactradiobutton.get_active():
            layoutstyle.apply(Layout.COMPACT)


    def on_StandardRadioButton_toggled(self):
        if standardradiobutton.get_active():
            layoutstyle.apply(Layout.STANDARD)

    def on_RefreshIP_Clicked(self):
        iplabel.set_text(Remote.get_ip())

builder = Gtk.Builder()
builder.add_from_file("config.ui")
window = builder.get_object("ConfigWindow")
window.show_all()

iplabel = builder.get_object("IPLabel")
Handler.on_RefreshIP_Clicked(None)

overclockgrid = builder.get_object("OverclockGrid")
cpuTempLabel = builder.get_object("cpuTempLabel")

standardradiobutton = builder.get_object("StandardRadioButton")
compactradiobutton = builder.get_object("CompactRadioButton")
miniradiobutton = builder.get_object("MiniRadioButton")

layoutstyle = Layout(builder)

builder.connect_signals(Handler)

if Overclock.is_raspi():
    Overclock.start_tempmonitor(cpuTempLabel)
else:
    overclockgrid.set_visible(False)

Gtk.main()
