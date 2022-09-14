from gi.repository import GLib
import subprocess
import os
import sys
import hint


class Display:
    WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
    PIBOOTCTL = GLib.find_program_in_path('pibootctl')
    MODE_ARG = 'video.firmware.mode'
    MEM_ARG = 'gpu.mem'
    CONFIG = '/boot/firmware/config.txt'
    PI_KMSMODE = os.path.join(WORKING_DIR, 'scripts', 'pi-kmsmode.sh')

    MODE = ['fkms', 'kms', 'legacy']
    MEM = ['128', '256', '512']

    def __init__(self, builder, device):
        self.displaygrid = builder.get_object("DisplayGrid")

        self.moderadiobuttons = [builder.get_object("FkmsRadioButton"),
                                 builder.get_object("KmsRadioButton"),
                                 builder.get_object("LegacyRadioButton")]

        self.memradiobuttons = [builder.get_object("Mem128RadioButton"),
                                builder.get_object("Mem256RadioButton"),
                                builder.get_object("Mem512RadioButton")]

        self.modebutton = builder.get_object("ModeButton")
        self.current_mode = ''
        self.membutton = builder.get_object("MemoryButton")
        self.current_mem = ''

        self.rebootlabel = builder.get_object("RebootLabel")
        self.rebootlabel.set_visible(False)

        self.app_statuslabel = builder.get_object("AppStatusLabel")
        tab = builder.get_object("DisplayTab")
        for button in self.moderadiobuttons:
            hint.add(button, self.app_statuslabel, hint.VIDEO_MODE)
        for button in self.memradiobuttons:
            hint.add(button, self.app_statuslabel, hint.GPU_MEMORY)
        hint.add(tab, self.app_statuslabel, hint.DISPLAY_TAB)
        hint.add(self.modebutton, self.app_statuslabel, hint.UPDATE_VIDEO)
        hint.add(self.membutton, self.app_statuslabel, hint.UPDATE_MEMORY)

        if device.pi_model is not None:
            if self.load_initial():
                self.modebutton.connect("clicked", self.on_modebutton_clicked)
                self.memsignal = self.membutton.connect(
                    "clicked", self.on_membutton_clicked)
            if not self.safe_to_change_mode():
                self.disable_mode_selection()
        else:
            # self.disable_controls()
            self.displaygrid.set_visible(False)

    def on_modebutton_clicked(self, *args):
        for i in range(len(self.moderadiobuttons)):
            if (self.moderadiobuttons[i].get_active()
                    and self.MODE[i] != self.current_mode):
                if (self.run_pibootctl('set', self.MODE_ARG+'='+self.MODE[i])
                        != 'error'):
                    self.current_mode = self.MODE[i]
                    self.rebootlabel.set_visible(True)

    def on_membutton_clicked(self, *args):
        for i in range(len(self.memradiobuttons)):
            if (self.memradiobuttons[i].get_active()
                    and self.MEM[i] != self.current_mem):
                if (self.run_pibootctl('set', self.MEM_ARG+'='+self.MEM[i])
                        != 'error'):
                    self.current_mem = self.MEM[i]
                    self.rebootlabel.set_visible(True)

    def disable_controls(self):
        for button in (self.moderadiobuttons + self.memradiobuttons):
            button.set_sensitive(False)
        hint.add(self.modebutton, self.app_statuslabel, hint.NO_PIBOOTCTL)
        hint.add(self.membutton, self.app_statuslabel, hint.NO_PIBOOTCTL)

    def find_value(self, result, key):
        # search pibootctl output for a key, and return the value
        lines = result.splitlines()
        find = key + "="
        for line in lines:
            if find in line:
                return line.split("=")[1]
        return None

    def load_initial(self):
        result = self.run_pibootctl('get', self.MODE_ARG,
                                    self.MEM_ARG, '--shell')
        # If pibootctl is missing or unsuccessful (i.e. run on a non-Pi device)
        if result == 'error':
            print("Unable to run pibootctl")
            self.disable_controls()
            return False
        else:
            mode = self.find_value(result, "video_firmware_mode")
            mem = self.find_value(result, "gpu_mem")
            for i in range(len(self.moderadiobuttons)):
                if mode == self.MODE[i]:
                    self.moderadiobuttons[i].set_active(True)
                    self.current_mode = self.MODE[i]
            for i in range(len(self.memradiobuttons)):
                if mem == self.MEM[i]:
                    self.memradiobuttons[i].set_active(True)
                    self.current_mem = self.MEM[i]
        return True

    def run_pibootctl(self, method, *params):
        if method == 'set':
            args = ['pkexec', self.PIBOOTCTL, method]
            # Fix for wrong overlay location - to be removed when resolved
            if len(params) >= 1 and "=kms" in params[0]:
                args = ['pkexec', self.PI_KMSMODE]
            # End fix
        else:
            args = [self.PIBOOTCTL, method]
        for item in params:
            args.append(item)

        try:
            output = subprocess.check_output(args, stderr=subprocess.STDOUT)
            output = output.decode("utf-8").strip('\'\n')
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
