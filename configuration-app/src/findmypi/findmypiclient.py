import socket
import threading
import time
import queue
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango


"""
Budgie Pi FindMyPi
Author: Samuel Lane
Copyright © 2021-2022 Ubuntu Budgie Developers
Website=https://ubuntubudgie.org
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version. This
program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details. You
should have received a copy of the GNU General Public License along with this
program.  If not, see <https://www.gnu.org/licenses/>.
"""


class FindMyPIClient:
    # Gets a list of Pis by one of two methods: scanning the network and
    # checking mac addresses, or having a UDP server running on the PI.
    # Used by the FindMyPiTreeView, but designed to be used independently

    PI_MACS = [
        ["4B or newer", ['dc:a6:32:']],
        ["3B+ or earlier", ['b8:27:eb:']],
        ["", ['28:cd:c1', 'e4:5f:01:']]
    ]

    def __init__(self, port=32323):
        self.ip_prefix = self._get_ip_prefix()
        self.max_threads = 255  # max number of threads to scan network
        self.timeout = 1        # how many seconds to wait for each ip
        self.port = port        # port to look for the UDP server on
        self.last_scan = 0.0    # time of last nmap scan
        self.prior_search = []  # the previous list of Pis found via scan

    def _get_ip_prefix(self):
        # Gets the client's IP prefix
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0].split('.')
        except Exception:
            IP = ['127', '0', '0']
        finally:
            s.close()
        IP_prefix = "{}.{}.{}.".format(IP[0], IP[1], IP[2])
        return IP_prefix

    def _get_model_by_mac(self, mac_addr):
        # Returns Pi model, based on mac address
        for model in self.PI_MACS:
            if any(mac.lower() in mac_addr.lower() for mac in model[1]):
                return " ".join(["Raspberry PI", model[0]])
        return ''

    def _run_nmap(self):
        # Run nmap to try to expose all mac addresses on network
        nmap = [GLib.find_program_in_path('nmap'), '-sn',
                self.ip_prefix+"0/24"]
        try:
            subprocess.check_output(nmap,
                                    stderr=subprocess.STDOUT).decode("utf-8")
        except Exception as e:
            print(e)

    def _run_arp(self):
        # Look at /proc/net/arp for the list of mac addresses for IPs
        output = []
        try:
            with open('/proc/net/arp', 'r') as arp_list:
                line = arp_list.readline().rstrip()
                while line:
                    if "00:00:00" not in line and "IP address" not in line:
                        output.append(line)
                    line = arp_list.readline().rstrip()
        except IOError as e:
            print("Error", e)
        return output

    def _answers_ping(self, ip):
        # Returns true if a Pi responds to ping
        # Used when arp temporarily doesn't show a pi, check before removing
        ping = ['timeout', '2', 'ping', '-c1', ip]
        try:
            output = subprocess.Popen(ping, stdout=subprocess.PIPE)
            output.communicate()
            if output.returncode == 0:
                return True
            else:
                return False
        except OSError:
            return False

    def get_list_from_mac(self):
        # scans using nmap / arp to look at mac address
        pi_list = []

        # after specified interval, run nmap
        now = time.time()
        if (now - self.last_scan) > 600.0:
            self.last_scan = now
            self._run_nmap()
            # slight delay between nmap and arp sometimes increases accuracy
            time.sleep(2)

        output = self._run_arp()
        for line in output:
            results = line.split()
            ip = results[0]
            mac = ''
            for i in range(len(results)):
                # make sure we are looking at a mac address
                if results[i].count(':') == 5:
                    mac = results[i]
            model = self._get_model_by_mac(mac)
            if mac != '' and model != '':
                item = [ip, mac, model]
                pi_list.append(item)

        # if a PI was on the last scan, but not the current scan, try to
        # ping it before removing (in case arp doesn't find it temporarily)
        for pi in self.prior_search:
            if pi not in pi_list and self._answers_ping(pi[0]):
                pi_list.append(pi)

        self.prior_search = pi_list.copy()

        return pi_list

    def _scan(self, ip_queue, results):
        # Scans an IP from the queue and checks if it is a PI
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        while True:
            ip = ip_queue.get()
            if ip is None:
                break
            try:
                sock.sendto("Are you a PI?".encode("utf-8"), (ip, self.port))
                response = sock.recvfrom(4096)
                msgdata = response[0].decode("utf-8")
                sender = (response[1][0])
                msg = "{},{}".format(sender, msgdata)
                # If local machine is running on a PI with server active,
                # don't add the localhost ip if there is a real IP also.
                if sender == "127.0.0.1":
                    if self.ip_prefix == "127.0.0.":
                        # If you are not connected to a network and you a PI
                        # scanning your own IP (why?), it's ok to add it
                        results.put(msg)
                    else:
                        # If 127.0.0.1 returns a result but have a real network
                        # IP also, do nothing for 127.0.0.1
                        pass
                else:
                    results.put(msg)
            except (socket.timeout, OSError):
                pass
        sock.close()

    def get_list_from_server(self):
        # Starts 'max_threads' number of threads to search for PIs
        self.ip_prefix = self._get_ip_prefix()
        ip_queue = queue.Queue()
        results = queue.Queue()
        pool = []
        threadcount = self.max_threads
        # if IP address is 127.0.0.1, just scan it, don't scan entire subnet
        if self.ip_prefix == '127.0.0.':
            threadcount = 1
            ip_queue.put('127.0.0.1')
        else:
            for i in range(1, 255):
                ip_queue.put(self.ip_prefix + '{0}'.format(i))
        for i in range(threadcount):
            t = threading.Thread(target=self._scan, args=(ip_queue, results),
                                 daemon=True)
            pool.append(t)
        for i in range(threadcount):
            ip_queue.put(None)
        for p in pool:
            p.start()
        for p in pool:
            p.join()
        pi_list = []
        while not results.empty():
            match = results.get().split(',')
            # if a machine answers twice (ie. if it's on wifi and ethernet)
            # only add the ip once (unlikely, but possible)
            if match not in pi_list:
                pi_list.append(match)
        return pi_list


class FindMyPiTreeView (Gtk.TreeView):
    # Gtk.Treeview that contains a list of discovered PIs, and continually
    # updates the list, and allows manual updating of list.

    def __init__(self, port=32323, method='server', frequency=120):
        super().__init__()

        self.port = port
        self.findpi = FindMyPIClient(port=self.port)
        self.pi_liststore = Gtk.ListStore(str, str, str)
        self.set_model(self.pi_liststore)
        self.set_size_request(290, 150)
        self.set_method(method)
        self.fields = ['IP Address', 'Host ID', 'Model']
        self.frequency = frequency
        self.started = False

        for i, field in enumerate(self.fields):
            cell = Gtk.CellRendererText()
            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            col = Gtk.TreeViewColumn(field, cell, text=i)
            col.set_sort_column_id(i)
            if i == 2:
                col.set_min_width(300)
            else:
                col.set_min_width(130)
            self.append_column(col)

    def set_method(self, method='server'):
        self.use_arp = True if method == 'mac' else False
        self.method_changed = True

    def start(self):
        # Starts the thread that updates the treeview
        if not self.started:
            self.started = True
            self.pi_liststore.append(['Searching', '', ''])
            self.thread = threading.Thread(target=self._search, daemon=True)
            self.thread.start()

    def _search(self):
        # Thread that automatically refreshes the list
        while True:
            self.refresh_list()
            time.sleep(self.frequency)

    def _update_list(self, pi_list):
        to_remove = []
        # If we switch methods we need to clear the list or else they will
        # display with the old information from the previous scans
        if self.method_changed:
            self.method_changed = False
            self.pi_liststore.clear()

        # Search liststore, generate list of iterations to be removed
        # Also removes existing PIs from the list of PIs to add
        iter_child = self.pi_liststore.get_iter_first()
        while iter_child:
            in_list = False
            ip = self.pi_liststore.get_value(iter_child, 0)
            for pi in pi_list:
                if pi[0] == ip:
                    in_list = True
                    pi_list.remove(pi)
            if not in_list:
                to_remove.append(iter_child)
            iter_child = self.pi_liststore.iter_next(iter_child)
        for child in to_remove:
            self.pi_liststore.remove(child)
        # Adds missing PIs to liststore
        for pi in pi_list:
            self.pi_liststore.append(pi)

    def get_list_from_server(self):
        # Returns list of connected PIs using FindMyPIClient
        return self.findpi.get_list_from_server()

    def get_list_from_mac(self):
        # Returns list of connected PIs using mac address search
        return self.findpi.get_list_from_mac()

    def refresh_list(self):
        # Refresh the treeview.  Can be called manually
        if self.use_arp:
            pi_list = self.findpi.get_list_from_mac()
        else:
            pi_list = self.findpi.get_list_from_server()
        GLib.idle_add(self._update_list, pi_list)

    def get_value_at_col(self, column):
        # Returns the value of the specified column currently selected row
        value = ""
        view_selection = self.get_selection()
        (model, tree_iter) = view_selection.get_selected()
        if tree_iter is not None:
            value = model.get_value(tree_iter, column)
        return value
