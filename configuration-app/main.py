import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

import dbus
import subprocess
import time
import os
import hint
import argparse
from remote import Remote
from overclock import Overclock
from layout import Layout
from display import Display
from findmypi import FindMyPi

class Handler:
    def on_ConfigWindow_destroy(self, *args):
        gsettings.set_boolean('runarmconfig',
            startlogincheckbutton.get_active())
        Gtk.main_quit()

    def on_ApplyButton_clicked(self):
        if miniradiobutton.get_active():
            layoutstyle.apply(Layout.MINI)
        elif compactradiobutton.get_active():
            layoutstyle.apply(Layout.COMPACT)
        else:
            layoutstyle.apply(Layout.STANDARD)

    def on_ConfigNotebook_switch_page(self, page, num):
        gsettings.set_int('lastpage', num)

    def on_RefreshIP_clicked(self):
        remote.refresh_ip()

def check_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-findpi-mode", action="store_true",
                        help="Start up in FindMyPi mode")
    parser.add_argument("--force-arm-mode", action="store_true",
                        help="Start in Config App mode")
    parser.add_argument("--force-model", choices=['CM4', '4', '400'])
    parser.add_argument("--model", action='append')
    cpu_arg = parser.add_argument("--cpuinfo", action='append')
    args = parser.parse_args()
    model_list = []
    models = args.model if args.model is not None else []
    cpu_infos = args.cpuinfo if args.cpuinfo is not None else []
    if len(cpu_infos) != len(models):
        parser.error("number of --cpuinfo and --model arguments must match")
    else:
        for i in range(len(models)):
            model_list.append([models[i], cpu_infos[i]])
    return args, model_list

args, model_list = check_args()
path = os.path.dirname(os.path.abspath(__file__))
resource = Gio.Resource.load(path + '/org.ubuntubudgie.armconfig.gresource')
Gio.resources_register(resource)
builder = Gtk.Builder.new_from_resource('/org/ubuntubudgie/armconfig/config.ui')
window = builder.get_object("ConfigWindow")
window.show_all()

standardradiobutton = builder.get_object("StandardRadioButton")
compactradiobutton = builder.get_object("CompactRadioButton")
miniradiobutton = builder.get_object("MiniRadioButton")

startlogincheckbutton = builder.get_object("StartLoginCheckButton")
gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')
startlogincheckbutton.set_active(gsettings.get_boolean('runarmconfig'))
notebook = builder.get_object('ConfigNotebook')
notebook.set_current_page(gsettings.get_int('lastpage'))

layoutstyle = Layout(builder)
overclock = Overclock(builder, args.force_model, model_list)

builder.connect_signals(Handler)
app_statuslabel = builder.get_object("AppStatusLabel")
hint.add(startlogincheckbutton, app_statuslabel, hint.AUTOSTART)

if ((overclock.pi_model is None and not args.force_arm_mode)
        or args.force_findpi_mode):
    findmypi = FindMyPi(builder)
else:
    remote = Remote(builder, overclock)
    display = Display(builder, overclock)

Gtk.main()
