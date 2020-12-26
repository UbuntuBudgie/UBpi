import socket
import subprocess

class Remote:

    def __init__(self,builder):
        self.iplabel = builder.get_object("IPLabel")
        self.refresh_ip()

        self.vncbutton = builder.get_object("VNCButton")
        self.vncbutton.connect('clicked', self.vncbuttonclicked)

        self.xrdpbutton = builder.get_object("XRDPButton")
        self.xrdpbutton.connect('clicked', self.xrdpbuttonclicked)

        self.xrdpstatuslabel = builder.get_object("XRDPStatusLabel")

        self.run_xrdp('status')

    def run_xrdp(self, param, root=False):

        if root:
            args = ['pkexec', '/usr/lib/budgie-desktop/arm/budgie-xrdp.sh', param]
        else:
            args = ['/usr/lib/budgie-desktop/arm/budgie-xrdp.sh', param]

        try:
            output = subprocess.check_output(args,
                stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")

        if 'root' in output:
            self.run_xrdp(param, root=True)
            self.run_xrdp('status')
        else:
            self.xrdpstatuslabel.set_text(output[0:50].rstrip('\n'))

    def xrdpbuttonclicked(self, *args):
        if 'service is ok' in self.xrdpstatuslabel.get_text():
            self.run_xrdp('disable')
        else:
            self.run_xrdp('enable')

    def vncbuttonclicked(self, *args):
        try:
            subprocess.run(['gnome-control-center', 'sharing'])
        except subprocess.CalledProcessError:
            pass

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def refresh_ip(self):
        self.iplabel.set_text(self.get_ip())
