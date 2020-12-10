from gi.repository import GLib

class Overclock:
    def _markup_temp(temp):
        if temp >= 75:
            color = "red"
        elif temp >= 60:
            color = "#CCCC00"
        else:
            color = "green"
        return "<b><span foreground='{}'>{}°C</span></b>".format(color,temp)

    def _temp_monitor(label):
        try:
            cputempfile = open("/sys/class/thermal/thermal_zone0/temp")
            cpu_temp = int(cputempfile.read()) // 1000
            cputempfile.close()
        except:
            # Should never happen, but just in case
            cpu_temp=0
        label.set_markup(Overclock._markup_temp(cpu_temp))
        return True

    def start_tempmonitor(label):
        GLib.timeout_add_seconds(1,Overclock._temp_monitor,label)

    def is_raspi():
        with open('/proc/cpuinfo','r') as cpufile:
            lines = cpufile.readlines()
            for line in lines:
                if "Raspberry Pi" in line:
                    return True
        return False
