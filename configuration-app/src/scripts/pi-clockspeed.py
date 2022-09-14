#!/usr/bin/env python3

"""
 Updates the /boot/firmware/config.txt file to the given clock speed.
 Modifies the voltage setting to match the given clock speed.

 Usage: pi-clockspeed get
        pi-clockspeed set <new speed>

       <new speed> must be 1500 / 1750 / 1800 / 2000 / 2150
"""

import re
import sys
import shutil
from os import path

# over_voltage setting to use for given clock speed
VOLTAGE = {'1500': '0',
           '1750': '2',
           '1800': '3',
           '2000': '6',
           '2150': '6'}

CONFIG_FILE = '/boot/firmware/config.txt'

""" - There are a few "Pi model"-specific sections in config.txt
    - Three different Pis are considered 'Model 4'
    - Settings changed via this will be done in the [all] section
      unless the keys exist in [pi4] already, and are not present in [all].
    - If using a pi 4, setting a clock speed of 1500 will remove the keys
      from config.txt.  However, since a pi400 defaults to 1800mhz, if used
      on a pi400, setting a clock speed of 1800 will remove the keys.
    - If keys are not present in the config.txt, the clock speed is
      reported as the default (1500 for pi4 and cm4, or 1800 for pi 400)
"""
RPI4 = 'pi4'      # Affects all Raspberry Pi 4s (includes CM4 and pi400)
RPI400 = 'pi400'  # Affects Raspberry Pi 400 only
CM4 = 'cm4'       # Affects Compute Module 4 only
ALL = 'all'       # Affects all Raspberry Pis regardless of model


class ConfigSection(list):

    def __init__(self, name=''):
        self.name = name

    def contains_key(self, key):
        for line in self:
            if line.split('=')[0] == key:
                return True
        return False

    def get_value(self, key):
        if self.contains_key(key):
            for line in self:
                if line.split('=')[0] == key:
                    return line.split('=')[1]
        else:
            return ''

    def update_key(self, key, value):
        found = False
        for i in range(len(self)):
            if self[i].split('=')[0] == key:
                found = True
                self[i] = '{}={}'.format(key, value)
        if not found:
            self.append('{}={}'.format(key, value))

    def clear_keys(self, keys):
        indexes = []
        for key in keys:
            for i in range(len(self)):
                if self[i].split('=')[0].strip() == key:
                    indexes.append(i)
        for i in sorted(indexes, reverse=True):
            del self[i]


class ConfigFile:

    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.sections = []
        self.section_count = 0

    def read(self):
        curr_section = ''
        try:
            with open(self.filename, 'r') as file:
                for read_line in file:
                    line = read_line.strip(' \n')
                    if self.active_section(line) is not None:
                        self.has_sections = True
                        curr_section = self.active_section(line)
                    self.add_to_section(curr_section, line)
        except FileNotFoundError:
            # file not found...default speed for model will be returned
            pass

    def add_to_section(self, section, line):
        # adds line to a section. If the section doesn't exist, it's created
        found = False
        for i in range(len(self.sections)):
            if self.sections[i].name == section:
                if self.sections[i][0] != line:
                    self.sections[i].append(line)
                found = True
        if not found:
            self.section_count += 1
            new = ConfigSection(section)
            new.append(line)
            self.sections.append(new)

    def has_section(self, section):
        # Checks if the loaded config has a given section name
        has = False
        for i in range(len(self.sections)):
            if self.sections[i].name == section:
                has = True
        return has

    def active_section(self, line):
        # if the current line is between brackets, it marks it as a section
        # and returns the section name.  Else it returns None
        search = re.search(r'\[(\w+)\]', line)
        if search is not None and line[0] != '#':
            return search.group(1)
        if search is not None and line[0] == '#'.strip():
            return '#{}'.format(search.group(1).strip())
        else:
            return None

    def get_sections(self, key):
        # returns all the sections in the loaded config file
        results = []
        for i in range(len(self.sections)):
            if self.sections[i].contains_key(key):
                results.append(self.sections[i].name)
        return results

    def get_speed(self, model):
        # Returns clock speed.  If its not set, returns defaults.
        # (1500 for pi4 and cm4, 1800 for pi 400)
        for section in self.sections:
            if (section.name in [ALL, RPI4, CM4] and
                    section.contains_key('arm_freq')):
                return section.get_value('arm_freq')
        if model == '400':
            return '1800'
        else:
            return '1500'

    def set_speed(self, model, speed):
        # Clears old keys in all conflicting sections, updates the new keys.
        # Prefers [all] but will use [pi4] if exclusively there already.
        arm_freq = self.get_sections('arm_freq')
        over_volt = self.get_sections('over_voltage')
        if ALL in arm_freq or ALL in over_volt:
            use_section = ALL
        elif RPI4 in arm_freq or RPI4 in over_volt:
            use_section = RPI4
        elif self.section_count == 1 and self.sections[0].name == '':
            use_section = ''
        else:
            use_section = ALL

        for section in self.sections:
            section.clear_keys(['arm_freq', 'over_voltage',
                                '#arm_freq', '#over_voltage'])
        if model in ['4', 'CM4', 'pi']:
            if speed != '1500':
                self.update_key(use_section, 'arm_freq', speed)
                self.update_key(use_section, 'over_voltage', VOLTAGE[speed])
        elif model == '400':
            # Pi400 defaults to 1800 - Don't underclock it
            if int(speed) > 1800:
                self.update_key(use_section, 'arm_freq', speed)
                self.update_key(use_section, 'over_voltage', VOLTAGE[speed])

    def update_key(self, section, key, value):
        # updates the key in the given section; creates the section if missing
        if not self.has_section(section):
            new = ConfigSection(section)
            new.append('[{}]'.format(section))
            self.sections.append(new)
        for i in range(len(self.sections)):
            if self.sections[i].name == section:
                self.sections[i].update_key(key, value)

    def save(self):
        # Saves config, but only backup succeeds or isn't needed
        lines = []
        saved = True
        if self.backup():
            for i in range(len(self.sections)):
                for j in self.sections[i]:
                    lines.append(j)
            try:
                with open(self.filename, 'w') as file:
                    for line in lines:
                        file.write(line+'\n')
            except (IOError, OSError):
                print('Unable to write file. Are you root?')
                saved = False
        else:
            print('Backup failed. Config file will not be updated.')
            saved = False
        return saved

    def backup(self):
        # return True if backup was successful, or if backup is not needed
        # because the does not exist.  Also creates empty file if missing.
        backup_name = self.filename + '.backup'
        if not path.exists(self.filename):
            # if config file doesn't exist, create it, but no need to back up
            return self.create_file()
        try:
            shutil.copy(self.filename, backup_name)
        except (IOError, OSError):
            print('Error backing up configuration. Are you root?')
            return False
        return True

    def create_file(self):
        # Create empty config file, return True if successful or False if not
        try:
            with open(self.filename, 'w') as configfile:
                configfile.write('')
        except (IOError, OSError):
            print('Cannot create {}. Are you root?'.format(self.filename))
            return False
        return True


def get_model():
    model = 'unknown'
    try:
        with open('/proc/cpuinfo') as cpufile:
            cpuinfo = cpufile.readlines()
            for line in cpuinfo:
                info = line.split(':')
                if info[0].strip() == 'Model':
                    model = info[1].strip()
                elif info[0].strip() == 'model name':
                    model = info[1].strip()
    except (IOError, OSError):
        pass
    if 'Raspberry Pi 400' in model:
        return('400')
    elif 'Raspberry Pi 4 ' in model:
        return('4')
    elif 'Compute Module 4 ' in model:
        return('CM4')
    # generic catch-all for Pis
    elif 'Raspberry Pi' in model:
        return('pi')
    else:
        return('unknown')


if __name__ == '__main__':

    model = get_model()
    if model == 'unknown':
        print('Error: Not running on a Raspberry Pi.')
        exit(1)

    config = ConfigFile(CONFIG_FILE)
    config.read()

    if len(sys.argv) == 1:
        print('Missing argument')
        exit(1)
    elif len(sys.argv) == 2 and sys.argv[1] == 'get':
        print(config.get_speed(model))
    elif len(sys.argv) == 3 and sys.argv[1] == 'set':
        if sys.argv[2] in VOLTAGE:
            config.set_speed(model, sys.argv[2])
            if config.save():
                print("Updated successfully!")
            else:
                exit(1)
        else:
            print('Bad speed value')
            exit(1)
    else:
        print('Bad or missing argument')
        exit(1)
