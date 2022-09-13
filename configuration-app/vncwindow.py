import socket
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class VncWindow(Gtk.Window):

    SETUPSCRIPT = '/usr/lib/budgie-desktop/arm/budgie-vnc.sh'

    def __init__(self, modal=True, transient_for=None):

        super().__init__()
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(modal)
        self.set_transient_for(transient_for)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_title("VNC Configuration")

        warnings = ['', '- Do not use root / login password for VNC',
                    '- VNC is restricted to local subnet by default',
                    '- VNC should only be enabled on trusted networks', '']
        self.set_default_size(170, 100)
        pwlabels = [Gtk.Label(label=" Enter a Password:"),
                    Gtk.Label(label="Confirm Password:")]
        grid = Gtk.Grid()
        self.passwds = []
        self.icons = []
        grid.attach(Gtk.Label(label=""), 0, 1, 3, 1)
        for i in range(2):
            pw = Gtk.Entry()
            pw.set_visibility(False)
            pw.connect("changed", self.on_entry, i)
            pw.connect("focus-in-event", self.on_field_change, i)
            pw.connect("activate", self.on_enter_press, i)
            icon = Gtk.Image.new_from_icon_name("button_cancel",
                                                Gtk.IconSize.LARGE_TOOLBAR)
            self.passwds.append(pw)
            self.icons.append(icon)
            grid.attach(pwlabels[i], 0, 1+i, 1, 1)
            grid.attach(self.passwds[i], 1, 1+i, 1, 1)
            grid.attach(self.icons[i], 2, 1+i, 1, 1)
        self.restrict_checkbutton = Gtk.CheckButton(
                                    label="Restrict to local network")
        self.restrict_checkbutton.set_active(True)
        self.prompt_checkbutton = Gtk.CheckButton(
                                  label="Prompt to allow connection")
        self.prompt_checkbutton.set_active(False)
        self.prompt_checkbutton.connect("toggled", self.on_prompt_toggled)
        self.viewonly_checkbutton = Gtk.CheckButton(
                                    label="Allow remote to view only")
        self.viewonly_checkbutton.set_active(False)
        self.localonly_checkbutton = Gtk.CheckButton(
                                     label="Allow localhost only (for SSH)")
        self.localonly_checkbutton.set_active(False)
        self.localonly_checkbutton.connect("toggled",
                                           self.on_localonly_toggled)
        self.ok_button = Gtk.Button(label="  OK  ")
        self.cancel_button = Gtk.Button(label="Cancel")
        grid.attach(self.restrict_checkbutton, 1, 3, 3, 1)
        grid.attach(self.prompt_checkbutton, 1, 4, 3, 1)
        grid.attach(self.viewonly_checkbutton, 1, 5, 3, 1)
        grid.attach(self.localonly_checkbutton, 1, 6, 3, 1)
        warning_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(self.ok_button, True, True, 5)
        button_box.pack_start(self.cancel_button, True, True, 5)
        self.ok_button.connect("clicked", self.on_ok_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        for warning in warnings:
            label = Gtk.Label(label=warning)
            label.set_halign(Gtk.Align.START)
            warning_box.pack_start(label, False, False, 0)
        grid.attach(warning_box, 0, 7, 3, 1)
        grid.attach(button_box, 1, 8, 2, 1)
        self.connect("delete-event", Gtk.main_quit)
        self.add(grid)

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def is_pw_valid(self, password):
        # Just to make sure no characters that might affect the bash script
        forbidden = [" ", "\\", "\"", "'"]
        if password == "":
            return False
        for char in forbidden:
            if char in password:
                return False
        return True

    def on_enter_press(self, entry, pw):
        # On enter press, move to next field
        if pw == 0:
            self.passwds[1].grab_focus()
        else:
            self.ok_button.grab_focus()

    def change_mark(self, icon, status):
        if status:
            icon.set_from_icon_name("emblem-checked",
                                    Gtk.IconSize.LARGE_TOOLBAR)
        else:
            icon.set_from_icon_name("button_cancel",
                                    Gtk.IconSize.LARGE_TOOLBAR)

    def button_enabled(self, mode):
        self.ok_button.set_sensitive(mode)
        pass

    def on_entry(self, entry, pw):
        if self.passwds[0].get_text() == "":
            self.change_mark(self.icons[0], False)
        if pw == 0 and self.is_pw_valid(self.passwds[0].get_text()):
            self.change_mark(self.icons[1], True)
            self.change_mark(self.icons[0], True)
        else:
            self.change_mark(self.icons[1], False)
        if pw == 1:
            if (self.passwds[1].get_text() == self.passwds[0].get_text()
                    and self.is_pw_valid(self.passwds[0].get_text())):
                self.change_mark(self.icons[1], True)
                self.button_enabled(True)
            else:
                self.change_mark(self.icons[1], False)
                self.button_enabled(False)
        else:
            if self.passwds[1].get_text() != self.passwds[0].get_text():
                self.change_mark(self.icons[1], False)
                self.button_enabled(False)
        if not self.is_pw_valid(self.passwds[0].get_text()):
            self.change_mark(self.icons[0], False)
            self.change_mark(self.icons[1], False)
            self.button_enabled(False)

    def on_field_change(self, entry, data, pw):
        if self.passwds[0].get_text() == "":
            self.change_mark(self.icons[0], False)
            self.button_enabled(False)
        if (self.passwds[0].get_text() != ""
                and self.is_pw_valid(self.passwds[0].get_text())):
            self.change_mark(self.icons[0], True)
        if (self.passwds[0].get_text() == self .passwds[1].get_text()
                and self.is_pw_valid(self.passwds[0].get_text())):
            self.change_mark(self.icons[1], True)
            self.button_enabled(True)
        else:
            self.change_mark(self.icons[1], False)
            self.button_enabled(False)

    def on_prompt_toggled(self, box):
        self.passwds[0].set_sensitive(not box.get_active())
        self.passwds[1].set_sensitive(not box.get_active())
        if box.get_active():
            self.button_enabled(True)
        elif (self.passwds[0].get_text() != ""
                and self.passwds[0].get_text() == self.passwds[1].get_text()):
            self.button_enabled(True)
        else:
            self.button_enabled(False)

    def on_localonly_toggled(self, toggle):
        self.restrict_checkbutton.set_sensitive(not toggle.get_active())

    def _setup_vnc(self, vnc_args):
        args = [self.SETUPSCRIPT, 'setup'] + vnc_args
        try:
            output = subprocess.check_output(
                     args, stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")

    def on_ok_clicked(self, button=None):
        vnc_args = []
        if self.prompt_checkbutton.get_active():
            vnc_args.append("--accept--")
        else:
            vnc_args.append(self.passwds[0].get_text())
        if self.viewonly_checkbutton.get_active():
            vnc_args.append("viewonly")
        else:
            vnc_args.append("control")
        if self.localonly_checkbutton.get_active():
            subnet = "localhost"
            vnc_args.append(subnet)
        elif self.restrict_checkbutton.get_active():
            # get the ip (needed to restrict VNC to local subnet)
            subnet = ".".join(self.get_ip().split(".", 3)[:-1]) + "."
            vnc_args.append(subnet)
        Gtk.main_quit()
        self._setup_vnc(vnc_args)

    def on_cancel_clicked(self, button):
        Gtk.main_quit()

    def run(self):
        self.show_all()
        Gtk.main()


def _main():
    win = VncWindow()
    win.set_type_hint(Gdk.WindowTypeHint.NORMAL)
    win.set_position(Gtk.WindowPosition.CENTER)
    win.run()
    win.destroy()


if __name__ == "__main__":
    _main()
