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

    def on_RefreshIP_clicked(self):
        remote.refresh_ip()

builder = Gtk.Builder()
builder.add_from_file("config.ui")
window = builder.get_object("ConfigWindow")
window.show_all()

standardradiobutton = builder.get_object("StandardRadioButton")
compactradiobutton = builder.get_object("CompactRadioButton")
miniradiobutton = builder.get_object("MiniRadioButton")

layoutstyle = Layout(builder)

remote = Remote(builder)
overclock = Overclock(builder)

builder.connect_signals(Handler)

Gtk.main()
