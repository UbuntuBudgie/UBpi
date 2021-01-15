from gi.repository import GLib
from overclock import Overclock
import subprocess

class Display:

    PIBOOTCTL = '/usr/bin/pibootctl'
    MODE_ARG  = 'video.firmware.mode'
    MEM_ARG   = 'gpu.mem'

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
        else:
            self.displaygrid.set_visible(False)

    def on_modebutton_clicked(self, *args):
        for i in range(len(self.moderadiobuttons)):
            if self.moderadiobuttons[i].get_active() and self.MODE[i] != self.current_mode:
                self.current_mode = self.MODE[i]
                self.run_pibootctl('set', self.MODE_ARG+'='+self.MODE[i])
                self.rebootlabel.set_visible(True)

    def on_membutton_clicked(self, *args):
        for i in range(len(self.memradiobuttons)):
            if self.memradiobuttons[i].get_active() and self.MEM[i] != self.current_mem:
                self.current_mem = self.MEM[i]
                self.run_pibootctl('set', self.MEM_ARG+'='+self.MEM[i])
                self.rebootlabel.set_visible(True)

    def load_initial(self):
        result = self.run_pibootctl('get', self.MODE_ARG)
        # Hide Display tab if pibootctl is mising
        if result == 'not found':
            print("Unable to run pibootctl")
            self.displaygrid.set_visible(False)
        else:
            for i in range(len(self.moderadiobuttons)):
                if result == self.MODE[i]:
                    self.moderadiobuttons[i].set_active(True)
                    self.current_mode = self.MODE[i]
            result = self.run_pibootctl('get', self.MEM_ARG)
            for i in range(len(self.memradiobuttons)):
                if result == self.MEM[i]:
                    self.memradiobuttons[i].set_active(True)
                    self.current_mem = self.MEM[i]

    def run_pibootctl(self, method, param):
        if method == 'set':
            args = ['pkexec']
        else:
            args = []
        args += [self.PIBOOTCTL, method, param]

        try:
            output = subprocess.check_output(args,
                stderr=subprocess.STDOUT).decode("utf-8").strip('\'\n')
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")
        except FileNotFoundError:
            output = 'not found'

        return output
