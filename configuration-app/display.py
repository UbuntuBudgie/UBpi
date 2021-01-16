from gi.repository import GLib
from overclock import Overclock
import subprocess

class Display:

    PIBOOTCTL = '/usr/bin/pibootctl'
    MODE_ARG  = 'video.firmware.mode'
    MEM_ARG   = 'gpu.mem'
    CONFIG    = '/boot/firmware/config.txt'

    MODE = ['fkms', 'kms', 'legacy']
    MEM  = ['128', '256', '512']

    def __init__(self,builder):
        self.displaygrid = builder.get_object("DisplayGrid")

        self.moderadiobuttons = [ builder.get_object("FkmsRadioButton"),
                                  builder.get_object("KmsRadioButton"),
                                  builder.get_object("LegacyRadioButton") ]

        self.memradiobuttons =  [ builder.get_object("Mem128RadioButton"),
                                  builder.get_object("Mem256RadioButton"),
                                  builder.get_object("Mem512RadioButton") ]

        self.modebutton = builder.get_object("ModeButton")
        self.modebutton.connect("clicked",self.on_modebutton_clicked)
        self.current_mode = ''

        self.membutton = builder.get_object("MemoryButton")
        self.membutton.connect("clicked", self.on_membutton_clicked)
        self.current_mem  = ''

        self.rebootlabel = builder.get_object("RebootLabel")
        self.rebootlabel.set_visible(False)

        if Overclock.is_raspi(None):
            self.load_initial()
            if not self.safe_to_change_mode():
                self.disable_mode_selection()
        else:
            self.displaygrid.set_visible(False)

    def on_modebutton_clicked(self, *args):
        for i in range(len(self.moderadiobuttons)):
            if self.moderadiobuttons[i].get_active() and self.MODE[i] != self.current_mode:
                if self.run_pibootctl('set', self.MODE_ARG+'='+self.MODE[i]) != 'error':
                    self.current_mode = self.MODE[i]
                    self.rebootlabel.set_visible(True)

    def on_membutton_clicked(self, *args):
        for i in range(len(self.memradiobuttons)):
            if self.memradiobuttons[i].get_active() and self.MEM[i] != self.current_mem:
                if self.run_pibootctl('set', self.MEM_ARG+'='+self.MEM[i]) != 'error': 
                    self.current_mem = self.MEM[i]
                    self.rebootlabel.set_visible(True)

    def load_initial(self):
        result = self.run_pibootctl('get', self.MODE_ARG, self.MEM_ARG, '--shell')
        # Hide Display tab if pibootctl is mising
        if result == 'error':
            print("Unable to run pibootctl")
            self.displaygrid.set_visible(False)
        else:
            mode, mem = result.replace('=','\n').splitlines()[1::2]
            for i in range(len(self.moderadiobuttons)):
                if mode == self.MODE[i]:
                    self.moderadiobuttons[i].set_active(True)
                    self.current_mode = self.MODE[i]
            for i in range(len(self.memradiobuttons)):
                if mem == self.MEM[i]:
                    self.memradiobuttons[i].set_active(True)
                    self.current_mem = self.MEM[i]

    def run_pibootctl(self, method, *params):
        if method == 'set':
            args = ['pkexec', self.PIBOOTCTL, method]
        else:
            args = [self.PIBOOTCTL, method]
        for item in params:
            args.append(item)

        try:
            output = subprocess.check_output(args,
                stderr=subprocess.STDOUT).decode("utf-8").strip('\'\n')
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")
            return 'error'
        except FileNotFoundError:
            return 'error'

        return output

    def disable_mode_selection(self):
        # Disable mode buttons when pibootctl can't be safely used
        for widget in ([self.modebutton] + self.moderadiobuttons):
            widget.set_sensitive(False)
            widget.set_tooltip_text("Can't change mode from vc4-kms-v3d-pi4")

    def safe_to_change_mode(self):
        # Check if video mode is currently vc4-kms-v3d-pi4
        safe = True
        try:
            with open(self.CONFIG) as file:
                content = file.readlines()
        except IOError:
            return True
        for line in content:
            if 'dtoverlay=vc4-kms-v3d-pi4' in line and line.strip()[0] != '#':
                safe = False
        return safe
