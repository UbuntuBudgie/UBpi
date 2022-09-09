#!/usr/bin/env python3

import socket
from select import select
import time


class FindMyPIServer:
    def __init__(self, port=32323):
        self.port = port
        self.host = socket.gethostname()
        self.model = self._get_model()
        self.ip = self.get_ip()
        self.run = False

    def update_ip(self):
        self.ip = self.get_ip()

    def _get_model(self):
        model = "unknown"
        try:
            with open("/proc/cpuinfo") as cpufile:
                cpuinfo = cpufile.readlines()
                for line in cpuinfo:
                    info = line.split(':')
                    if info[0].strip() == "Model":
                        model = info[1].strip()
                    elif info[0].strip() == "model name":
                        model = info[1].strip()
        except Exception as e:
            print('Unable to get CPU info:', e)
        return model

    def get_ip(self):
        # Return current IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def run_server(self):
        self.run = True
        self.ip = self.get_ip()
        self.hostname = socket.gethostname()
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.udp.bind(('0.0.0.0', self.port))
        except OSError:
            print("Socket could not be opened")
        else:
            print("FindMyPI server started")
            self.input = [self.udp]
            while self.run:
                inputready, outputready, exceptready = select(self.input,
                                                              [], [], 2)
                for s in inputready:
                    if s == self.udp:
                        data, addr = s.recvfrom(4096)
                        msg = data.decode("utf-8")
                        if msg == "Are you a PI?":
                            reply = "{},{}".format(self.host, self.model)
                            sent = s.sendto(reply.encode(), addr)
                    else:
                        print("unknown socket:")
            self.udp.close()


if __name__ == "__main__":
    findmypiserver = FindMyPIServer(32323)
    findmypiserver.run_server()
