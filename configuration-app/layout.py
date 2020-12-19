import gi
import dbus
import subprocess
import time
import socket

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib

class Layout:
    _fontname="Sawasdee "

    # types of layouts that can be applied
    MINI=1
    COMPACT=2
    STANDARD=3

    def __init__(self, builder):
        self.logoutloginlabel = builder.get_object("LogoutLoginLabel")
        self.logoutloginlabel.set_visible(False)

        self.standardradiobutton = builder.get_object("StandardRadioButton")
        self.compactradiobutton = builder.get_object("CompactRadioButton")
        self.miniradiobutton = builder.get_object("MiniRadioButton")

        gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')

        layout = gsettings.get_string('layout-style')
        if layout == "standard":
            self.standardradiobutton.set_active(True)
        elif layout == "compact":
            self.compactradiobutton.set_active(True)
        elif layout == "mini":
            self.miniradiobutton.set_active(True)
        else:
            raise SystemExit('Unknown layout to initialise')

        width, height, xoffset, yoffset = self._get_resolution()

        resolution = builder.get_object("ResolutionLabel")
        resolution.set_text(str(width) + " x " + str(height))

        standard_recommendation = builder.get_object("StandardRecommendedLabel")
        compact_recommendation = builder.get_object("CompactRecommendedLabel")
        mini_recommendation = builder.get_object("MiniRecommendedLabel")

        print(height)
        if height >= 900:
            standard_recommendation.set_text("Recommended")
            compact_recommendation.set_text("")
            mini_recommendation.set_text("")
        elif height >= 768:
            standard_recommendation.set_text("")
            compact_recommendation.set_text("Recommended")
            mini_recommendation.set_text("")
        else:
            standard_recommendation.set_text("")
            compact_recommendation.set_text("")
            mini_recommendation.set_text("Recommended")

    def apply(self, layouttype):

        if layouttype == Layout.MINI:
            showtime = ["42", "18", -14]
        elif layouttype == Layout.COMPACT:
            showtime = ["60", "24", -25]
        elif layouttype == Layout.STANDARD:
            # nothing really to-do
            print('i')
        else:
            raise SystemExit('unknown compacy layout')

        if layouttype == Layout.STANDARD:
            self._reset_desktopfonts()
            self._reset_showtime()
            self._reset_theme()
            self._apply_layout("ubuntubudgie")
        else:
            self._set_showtime(self._fontname+showtime[0], self._fontname+showtime[1], showtime[2])
            self._set_desktopfonts(layouttype)
            self._set_theme()
            self._apply_layout("ubuntubudgiecompact")

            time.sleep(5)
            self._set_panel_key('autohide', 'automatic')
            self._set_compact_menu()

        self.logoutloginlabel.set_visible(True)
        self._save_layout(layouttype)

    def _save_layout(self, layouttype):
        gsettings = Gio.Settings.new('org.ubuntubudgie.armconfig')

        if layouttype == Layout.STANDARD:
            layoutstr = 'standard'
        elif layouttype == Layout.COMPACT:
            layoutstr = 'compact'
        elif layouttype == Layout.MINI:
            layoutstr = 'mini'
        else:
            raise SystemExit('unknown layout to save')

        gsettings.set_string('layout-style', layoutstr)

    def _set_panel_key(self, key, value):
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

    def _set_desktopfonts(self, layouttype):

        if layouttype == Layout.MINI:
            font_size = "8"
            mono_size = "10"

        if layouttype == Layout.COMPACT:
            font_size = "10"
            mono_size = "12"

        settings = Gio.Settings.new("org.gnome.desktop.wm.preferences")
        settings.set_string("titlebar-font", "Noto Sans Bold "+font_size)

        settings = Gio.Settings.new("org.gnome.desktop.interface")
        settings.set_string("monospace-font-name", "Ubuntu Mono "+mono_size)
        settings.set_string("font-name", "Noto Sans "+font_size)
        settings.set_string("document-font-name" , "Noto Sans "+font_size)

        settings = Gio.Settings.new("org.nemo.desktop")
        settings.set_string("font", "Noto Sans "+font_size)

    def _set_theme(self):
        settings = Gio.Settings.new("org.gnome.desktop.interface")
        settings.set_string("gtk-theme", "Pocillo-dark-slim")

        settings = Gio.Settings.new("org.gnome.desktop.wm.preferences")
        settings.set_string("theme", "Pocillo-dark-slim")

    def _reset_desktopfonts(self):
        settings = Gio.Settings.new("org.gnome.desktop.wm.preferences")
        settings.reset("titlebar-font")

        settings = Gio.Settings.new("org.gnome.desktop.interface")
        settings.reset("monospace-font-name")
        settings.reset("font-name")
        settings.reset("document-font-name")

        settings = Gio.Settings.new("org.nemo.desktop")
        settings.reset("font")

    def _reset_showtime(self):
        settings = Gio.Settings.new("org.ubuntubudgie.plugins.budgie-showtime")
        settings.reset("timefont")
        settings.reset("datefont")
        settings.reset("linespacing")

    def _reset_theme(self):
        settings = Gio.Settings.new("org.gnome.desktop.interface")
        settings.reset("gtk-theme")

        settings = Gio.Settings.new("org.gnome.desktop.wm.preferences")
        settings.reset("theme")

    def _get_resolution(self):
        dsp = Gdk.Display.get_default()
        prim = dsp.get_primary_monitor()
        geo = prim.get_geometry()
        xoffset = geo.x
        yoffset = geo.y
        width = geo.width
        height = geo.height
        return (width, height, xoffset, yoffset)