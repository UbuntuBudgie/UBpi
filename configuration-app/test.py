import gi
import dbus
import subprocess
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio

class Layout:
    def getres(self):
        dsp = Gdk.Display.get_default()
        prim = dsp.get_primary_monitor()
        geo = prim.get_geometry()
        xoffset = geo.x
        yoffset = geo.y
        width = geo.width
        height = geo.height
        return (width, height, xoffset, yoffset)

    def set_panel_key(self, key, value):
        # panel keys are relocatable - so need to loop through all panels
        # and set the key to the value given

        gsettings = Gio.Settings.new('com.solus-project.budgie-panel')

        panels = gsettings.get_strv('panels')

        for panel in panels:
            gsettings = Gio.Settings.new_with_path('com.solus-project.budgie-panel.panel',
                                                   '/com/solus-project/budgie-panel/panels/{' + panel + '}/')
            if type(value) == bool:
                gsettings.set_boolean(key, value)
            elif type(value) == int:
                gsettings.set_int(key, value)
            else:
                gsettings.set_string(key, value)

class CompactLayout(Layout):
    _fontname="Sawasdee "
    _compact_layout="ubuntubudgiecompact"

    def _apply_layout(self, layout):

        # well-known name for our program
        ECHO_BUS_NAME = 'org.UbuntuBudgie.ExtrasDaemon'

        # interfaces implemented by some objects in our program
        ECHO_INTERFACE = 'org.UbuntuBudgie.ExtrasDaemon'

        # paths to some objects in our program
        ECHO_OBJECT_PATH = '/org/ubuntubudgie/extrasdaemon'

        bus = dbus.SessionBus()

        try:
            proxy = bus.get_object(ECHO_BUS_NAME, ECHO_OBJECT_PATH)
        except dbus.DBusException as e:
            # There are actually two exceptions thrown:
            # 1: org.freedesktop.DBus.Error.NameHasNoOwner
            #   (when the name is not registered by any running process)
            # 2: org.freedesktop.DBus.Error.ServiceUnknown
            #   (during auto-activation since there is no .service file)
            # TODO figure out how to suppress the activation attempt
            # also, there *has* to be a better way of managing exceptions
            if e._dbus_error_name != \
                    'org.freedesktop.DBus.Error.ServiceUnknown':
                raise
            if e.__context__._dbus_error_name != \
                    'org.freedesktop.DBus.Error.NameHasNoOwner':
                raise
            print('client: No one can hear me!!')
        else:
            iface = dbus.Interface(proxy, ECHO_INTERFACE)

            iface.ResetLayout(layout)

    def _set_compact_menu(self):
        args = ['/usr/lib/budgie-desktop/arm/reset.sh', 'true']

        try:
            subprocess.run(args)
        except subprocess.CalledProcessError:
            pass

    def _set_showtime(self, timefont, datefont, linespacing):
        settings = Gio.Settings.new("org.ubuntubudgie.plugins.budgie-showtime")
        settings.set_string("timefont", timefont)
        settings.set_string("datefont", datefont)
        settings.set_int("linespacing", linespacing)

    def apply(self):
        self._set_showtime(self._fontname+"42", self._fontname+"18", -14)
        self._apply_layout(self._compact_layout)
        time.sleep(5)
        self.set_panel_key('autohide', 'automatic')
        self._set_compact_menu()

    def ask_to_reset(self):
        dialog = Gtk.MessageDialog(
            transient_for=window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Reset layout to fit screen resolution?",
        )
        dialog.format_secondary_text(
            "The default layout and fonts are optimised for a standard desktop screen resolution. ......"
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.apply()
        elif response == Gtk.ResponseType.CANCEL:
            print("dialog closed by clicking CANCEL button")

        dialog.destroy()


class DefaultLayout(Layout):
    def apply(self):
        print("hi")

class Handler:
    def on_ConfigWindow_destroy(self, *args):
        Gtk.main_quit()

    def on_CompactButton_clicked(self):
        compactlayout.apply()

    def on_DefaultButton_clicked(self):
        defaultlayout.apply()

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

if height <= 1768:
    compactlayout.ask_to_reset()

Gtk.main()