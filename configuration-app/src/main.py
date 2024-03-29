import os
import sys
from lib import hint
import argparse
from modules.remote import Remote
from modules.overclock import Overclock
from modules.layout import Layout
from modules.display import Display
from findmypi.findmypi import FindMyPi
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


"""
Budgie Pi Configuration App
Copyright © 2021-2022 Ubuntu Budgie Developers
Website=https://ubuntubudgie.org
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version. This
program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details. You
should have received a copy of the GNU General Public License along with this
program.  If not, see <https://www.gnu.org/licenses/>.
"""


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
    parser.add_argument("--get-model-info", action="store_true",
                        help="Display the model information")
    parser.add_argument("--force-model", choices=['CM4', '4', '400'],
                        help="Recognize this machine as the specifed model")
    parser.add_argument("--model", action='append')
    parser.add_argument("--cpuinfo", action='append',
                        help="When --cpuinfo is used with --model, a matching"
                        + " CPU will be recognized as the specified model")
    parsed_args = parser.parse_args()
    pi_model_list = []
    models = parsed_args.model if parsed_args.model is not None else []
    cpu_infos = parsed_args.cpuinfo if parsed_args.cpuinfo is not None else []
    if len(cpu_infos) != len(models):
        parser.error("number of --cpuinfo and --model arguments must match")
    else:
        for index, model in enumerate(models):
            pi_model_list.append([model, cpu_infos[index]])
    return parsed_args, pi_model_list


args, model_list = check_args()
path = os.path.dirname(os.path.abspath(__file__))
resource = Gio.Resource.load(path + '/org.ubuntubudgie.armconfig.gresource')
Gio.resources_register(resource)
builder = Gtk.Builder.new_from_resource(
    '/org/ubuntubudgie/armconfig/config.ui')
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

if args.get_model_info:
    pimodel = overclock.get_pimodel_line().split(':')
    if len(pimodel) > 1:
        sys.exit(pimodel[1].strip() + " " + overclock.get_model_memory())
    else:
        sys.exit("Unable to get Pi model info. Is this a Raspberry Pi?")

if ((overclock.pi_model is None and not args.force_arm_mode)
        or args.force_findpi_mode):
    findmypi = FindMyPi(builder)
else:
    remote = Remote(builder)
    display = Display(builder, overclock)

Gtk.main()
