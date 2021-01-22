from gi.repository import GLib
import subprocess


class Overclock:

    PI_CLOCKSPEED = '/usr/lib/budgie-desktop/arm/pi-clockspeed.py'
    PI_SPEEDS = ['1500', '1800', '2000']

    def __init__(self, builder):
        self.overclock_tab = builder.get_object("OverclockGrid")
        if self.is_raspi():
            self._setup_overclock(builder)
        else:
            self.overclock_tab.set_visible(False)

    def _markup_temp(self, temp):
        if temp >= 75:
            color = "red"
        elif temp >= 60:
            color = "#CCCC00"
        else:
            color = "green"
        return "<b><span foreground='{}'>{}°C</span></b>".format(color, temp)

    def _temp_monitor(self):
        try:
            cputempfile = open("/sys/class/thermal/thermal_zone0/temp")
            cpu_temp = int(cputempfile.read()) // 1000
            cputempfile.close()
        except (IOError, OSError):
            # Should never happen, but just in case
            cpu_temp = 0
        self.cputemp_label.set_markup(self._markup_temp(cpu_temp))
        return True

    def _setup_overclock(self, builder):
        self.cputemp_label = builder.get_object("cpuTempLabel")
        self.overclockbutton = builder.get_object("OverclockButton")
        self.speedlabel = builder.get_object("SpeedLabel")
        self.speed_radiobuttons = [
                builder.get_object("Default_Speed_radiobutton"),
                builder.get_object("Mid_Speed_radiobutton"),
                builder.get_object("High_Speed_radiobutton")]
        self.start_tempmonitor()
        self.overclockbutton.connect("clicked", self.on_overclockbutton_clicked)
        self.currentspeeed = self._run_piclockspeed('get')
        self._set_currentspeed()
        if self.get_pimodel() == '400':
            # if Pi is Model 400, disable 1.5GHz, since its default is 1.8GHz
            self.speed_radiobuttons[0].set_sensitive(False)

    def start_tempmonitor(self):
        GLib.timeout_add_seconds(1, self._temp_monitor)

    def is_raspi(self):
        if self.get_pimodel() != '':
            return True
        else:
            return False

    def get_pimodel(self):
        model = ''
        with open('/proc/cpuinfo', 'r') as cpufile:
            lines = cpufile.readlines()
            for line in lines:
                if "Raspberry Pi 400" in line:
                    model = '400'
                elif "Raspberry Pi 4 " in line:
                    model = 'pi4'
        return model

    def _set_currentspeed(self):
        speed = int(self.currentspeeed)/1000
        self.speedlabel.set_text(" {}GHz".format(speed))
        for i in range(len(self.speed_radiobuttons)):
            if self.currentspeeed == self.PI_SPEEDS[i]:
                self.speed_radiobuttons[i].set_active(True)

    def on_overclockbutton_clicked(self, button):
        for i in range(len(self.speed_radiobuttons)):
            if (self.speed_radiobuttons[i].get_active()
                    and self.currentspeeed != self.PI_SPEEDS[i]):
                status = self._run_piclockspeed('set', self.PI_SPEEDS[i])
                if status != 'error':
                    self.currentspeeed = self.PI_SPEEDS[i]
                    self._set_currentspeed()

    def _run_piclockspeed(self, method, *params):
        if method == 'set':
            args = ['pkexec', 'python3', self.PI_CLOCKSPEED, method]
        else:
            args = ['python3', self.PI_CLOCKSPEED, method]
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
