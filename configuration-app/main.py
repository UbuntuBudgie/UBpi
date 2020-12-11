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

    def on_MiniRadioButton_toggled(self):
        if miniradiobutton.get_active():
            compactlayout.apply(CompactLayout.MINI)

    def on_CompactRadioButton_toggled(self):
        if compactradiobutton.get_active():
            compactlayout.apply(CompactLayout.COMPACT)


    def on_StandardRadioButton_toggled(self):
        if standardradiobutton.get_active():
            defaultlayout.apply()

        
    def on_RefreshIP_Clicked(self):
        iplabel.set_text(Remote.get_ip())

builder = Gtk.Builder()
builder.add_from_file("config.ui")
builder.connect_signals(Handler)

window = builder.get_object("ConfigWindow")

window.show_all()
logoutloginlabel = builder.get_object("LogoutLoginLabel")
logoutloginlabel.set_visible(False)

iplabel = builder.get_object("IPLabel")
Handler.on_RefreshIP_Clicked(None)

overclockgrid = builder.get_object("OverclockGrid")
cpuTempLabel = builder.get_object("cpuTempLabel")

standardradiobutton = builder.get_object("StandardRadioButton")
compactradiobutton = builder.get_object("CompactRadioButton")
miniradiobutton = builder.get_object("MiniRadioButton")

compactlayout = CompactLayout(builder)
defaultlayout = DefaultLayout(builder)

if Overclock.is_raspi():
    Overclock.start_tempmonitor(cpuTempLabel)
else:
    overclockgrid.set_visible(False)

Gtk.main()
