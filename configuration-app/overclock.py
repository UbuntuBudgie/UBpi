from gi.repository import GLib

class Overclock:

    def __init__(self,builder):
        self.cputemp_label = builder.get_object("cpuTempLabel")
        self.overclock_tab = builder.get_object("OverclockGrid")
        if self.is_raspi():
            self.start_tempmonitor()
        else:
            self.overclock_tab.set_visible(False)

    def _markup_temp(self,temp):
        if temp >= 75:
            color = "red"
        elif temp >= 60:
            color = "#CCCC00"
        else:
            color = "green"
        return "<b><span foreground='{}'>{}°C</span></b>".format(color,temp)

    def _temp_monitor(self):
        try:
            cputempfile = open("/sys/class/thermal/thermal_zone0/temp")
            cpu_temp = int(cputempfile.read()) // 1000
            cputempfile.close()
        except:
            # Should never happen, but just in case
            cpu_temp=0
        self.cputemp_label.set_markup(self._markup_temp(cpu_temp))
        return True

    def start_tempmonitor(self):
        GLib.timeout_add_seconds(1,self._temp_monitor)

    def is_raspi(self):
        with open('/proc/cpuinfo','r') as cpufile:
            lines = cpufile.readlines()
            for line in lines:
                if "Raspberry Pi" in line:
                    return True
        return False

