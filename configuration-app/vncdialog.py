import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

class VncDialog(Gtk.Dialog):
    def __init__(self):
        super().__init__(title="Configure VNC Password", flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        warnings = ['','- Do not use root / login password for VNC',
                    '- VNC is restricted to local subnet by default',
                    '- VNC should only be enabled on trusted networks','']
        self.set_default_size(170, 100)
        pwlabels = [Gtk.Label(label=" Enter a Password:"), Gtk.Label(label="Confirm Password:")]
        grid = Gtk.Grid()
        self.passwds = []
        self.icons = []
        grid.attach(Gtk.Label(label=""),0,1,3,1)
        for i in range(2):
            pw = Gtk.Entry()
            pw.set_visibility(False)
            pw.connect("changed", self.on_entry, i)
            pw.connect("focus-in-event", self.on_field_change, i)
            pw.connect("activate", self.on_enter_press, i)
            icon = Gtk.Image.new_from_icon_name("button_cancel", Gtk.IconSize.LARGE_TOOLBAR)
            self.passwds.append(pw)
            self.icons.append(icon)
            grid.attach(pwlabels[i],0,1+i,1,1)
            grid.attach(self.passwds[i],1,1+i,1,1)
            grid.attach(self.icons[i],2,1+i,1,1)
        self.restrict_checkbutton = Gtk.CheckButton(label="Restrict to local network")
        self.restrict_checkbutton.set_active(True)
        self.prompt_checkbutton = Gtk.CheckButton(label="Prompt to allow connection")
        self.prompt_checkbutton.set_active(False)
        self.prompt_checkbutton.connect("toggled", self.on_prompt_toggled)
        self.viewonly_checkbutton = Gtk.CheckButton(label="Allow remote to view only")
        self.viewonly_checkbutton.set_active(False)
        grid.attach(self.restrict_checkbutton,1,3,3,1)
        grid.attach(self.prompt_checkbutton,1,4,3,1)
        grid.attach(self.viewonly_checkbutton,1,5,3,1)
        box = self.get_content_area()
        warning_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        for x in range(len(warnings)):
            label = Gtk.Label(label=warnings[x])
            label.set_halign(Gtk.Align.START)
            warning_box.pack_start(label, False, False, 0)
        grid.attach(warning_box, 0, 6, 3, 1)
        box.add(grid)
        self.set_response_sensitive(Gtk.ResponseType.OK, False)
        self.connect("response", self.on_response)
        self.show_all()

    def is_pw_valid(self, password):
        # Just check to make sure no characters that might affect the bash script
        forbidden = [" ", "\\", "\"", "'"]
        if password == "":
            return False
        for char in forbidden:
            if char in password:
                return False
        return True

    def on_enter_press(self, entry, pw):
        # On enter press, move to next field, or activate dialog box if password is ok
        if pw == 0:
            self.passwds[1].grab_focus()
        elif (self.passwds[0].get_text() == self.passwds[1].get_text() and self.is_pw_valid(self.passwds[0].get_text())):
            self.response(Gtk.ResponseType.OK)

    def on_response(self, widget, response_id):
        self.result = self.passwds[0].get_text()

    def get_result(self):
        if self.prompt_checkbutton.get_active():
            return "--accept--"
        return self.result

    def get_restrict(self):
        return self.restrict_checkbutton.get_active()

    def get_viewonly(self):
        return self.viewonly_checkbutton.get_active()

    def change_mark(self, icon, status):
        if status:
            icon.set_from_icon_name("emblem-checked", Gtk.IconSize.LARGE_TOOLBAR)
        else:
            icon.set_from_icon_name("button_cancel", Gtk.IconSize.LARGE_TOOLBAR)

    def button_enabled(self, mode):
        self.set_response_sensitive(Gtk.ResponseType.OK, mode)

    def on_entry (self, entry, pw):
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

    def on_field_change (self, entry, data, pw):
        if self.passwds[0].get_text() == "":
            self.change_mark(self.icons[0], False)
            self.button_enabled(False)
        if self.passwds[0].get_text() != "" and self.is_pw_valid(self.passwds[0].get_text()):
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
        elif self.passwds[0].get_text() != "" and self.passwds[0].get_text() == self.passwds[1].get_text():
            self.button_enabled(True)
        else:
            self.button_enabled(False)