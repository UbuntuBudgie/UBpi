from gi.repository import GLib
import subprocess
import os
import hint


class Overclock:

    PI_CLOCKSPEED = '/usr/lib/budgie-desktop/arm/pi-clockspeed.py'
    PI_SPEEDS = ['1500', '1800', '2000']
    PI_1800_MODELS = ['400']  # models which run at 1800 by default

    def __init__(self, builder, forcedmodel=None, model_list=None):
        self.overclock_tab = builder.get_object("OverclockGrid")
        self.model_list = model_list
        if forcedmodel is None:
            self.pi_model = self.get_pimodel()
        else:
            self.pi_model = forcedmodel
        if self.pi_model:
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
        self.model_label = builder.get_object("ModelLabel")
        self.memory_label = builder.get_object("MemoryLabel")
        self.speedlabel = builder.get_object("SpeedLabel")
        self.speed_radiobuttons = [
                builder.get_object("Default_Speed_radiobutton"),
                builder.get_object("Mid_Speed_radiobutton"),
                builder.get_object("High_Speed_radiobutton")]
        self.rebootlabel = builder.get_object("OCRebootLabel")
        self.rebootlabel.set_visible(False)
        self.start_tempmonitor()
        self.currentspeed = self._run_piclockspeed('get')
        self._set_currentspeed()
        if self.pi_model in self.PI_1800_MODELS:
            # if Pi is Model 400, disable 1.5GHz, since its default is 1.8GHz
            self.speed_radiobuttons[0].set_sensitive(False)
        model = self.get_pimodel_line().split(':')
        if len(model) > 1:
            self.model_label.set_text(model[1])
        self.memory_label.set_text(self.get_model_memory())

        app_statuslabel = builder.get_object("AppStatusLabel")
        tab = builder.get_object("OverclockTab")
        cputempbox = builder.get_object("CPUTempBox")
        hint.add(tab, app_statuslabel, hint.OVERCLOCK_TAB)
        hint.add(cputempbox, app_statuslabel, hint.CPU_TEMP)
        for button in self.speed_radiobuttons:
            hint.add(button, app_statuslabel, hint.CPU_SPEEDS)
        if os.path.exists('/boot/firmware/config.txt'):
            hint.add(self.overclockbutton, app_statuslabel, hint.SPEED_BUTTON)
            self.overclockbutton.connect("clicked", self.on_overclockbutton_clicked)
        else:
            for button in self.speed_radiobuttons:
                button.set_sensitive(False)
            hint.add(self.overclockbutton, app_statuslabel, hint.NO_CONFIGTXT)
            self.speedlabel.set_text("")

    def start_tempmonitor(self):
        GLib.timeout_add_seconds(1, self._temp_monitor)

    def get_pimodel_line(self):
        model_line = ''
        with open('/proc/cpuinfo', 'r') as cpufile:
            lines = cpufile.readlines()
            for line in lines:
                if line.split(':')[0].rstrip(' \t\n') in ["Model", "model name"]:
                    model_line = line.strip()
                    break
        return model_line

    def get_pimodel(self):
        model_line = self.get_pimodel_line()
        for i in range(len(self.model_list)):
            if self.model_list[i][1] in model_line:
                return self.model_list[i][0]
        if "Raspberry Pi 400" in model_line:
            return '400'
        elif "Raspberry Pi 4 " in model_line:
            return '4'
        elif "Pi Compute Module 4" in model_line:
            return 'CM4'
        # Generic catch-all Pis
        elif "Raspberry Pi" in model_line:
            return 'Pi'
        return None

    def get_model_memory(self):
        with open('/proc/meminfo', 'r') as memfile:
            lines = memfile.readlines()
            for line in lines:
                if line.split(':')[0].rstrip(' \t\n') == "MemTotal":
                    mem_line = line.split()
                    break
        if len(mem_line) > 1:
            try:
               memory = int(round(float(mem_line[1]) / 976600))
               return str(memory) + "GB"
            except:
               pass
        return "unknown"

    def _set_currentspeed(self):
        if self.currentspeed == 'error' or self.currentspeed == '1500':
            self.currentspeed = '1800' if self.pi_model == '400' else '1500'
        speed = int(self.currentspeed)/1000
        self.speedlabel.set_text(" {}GHz".format(speed))
        for i in range(len(self.speed_radiobuttons)):
            if self.currentspeed == self.PI_SPEEDS[i]:
                self.speed_radiobuttons[i].set_active(True)

    def on_overclockbutton_clicked(self, button):
        for i in range(len(self.speed_radiobuttons)):
            if (self.speed_radiobuttons[i].get_active()
                    and self.currentspeed != self.PI_SPEEDS[i]):
                status = self._run_piclockspeed('set', self.PI_SPEEDS[i])
                if status != 'error':
                    self.currentspeed = self.PI_SPEEDS[i]
                    self._set_currentspeed()
                    self.rebootlabel.set_visible(True)

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
