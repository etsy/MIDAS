#!/usr/bin/env python
"""
This is a set of helper functions for network utilities
"""

from system import shell_out
from datetime import datetime
import re


def get_ifconfig():
    """
    Returns a JSON array of `ifconfig`
    """
    ifconfig = shell_out("ifconfig -a")
    json = {}
    if ifconfig:
        for i in ifconfig:
            if not i.startswith('\t'):
                interface = i.split(':')[0]
                json[interface] = {}
                curr = interface
            else:
                i = i[1:]
                i_space = i.find(' ')
                i_equals = i.find('=')
                greater_than = i_space if i_space > i_equals else i_equals
                k = i[:greater_than].strip(':')
                j = i[greater_than:].split(' ')
                if j[0] == '':
                    j = j[1::]
                json[curr][k] = j
    return json


def parse_date(line):
    """
    Parse the date from a syslog line
    """
    try:
        date = "%s %s" % (
            str(datetime.today().year),
            ' '.join(line.split(' ')[:3])
        )
        ret = datetime.strptime(date, "%Y %b %d %H:%M:%S")
    except IOError:
        ret = None
    except Exception:
        ret = None
    if ret:
        today = datetime.today()
        if (ret.month > today.month) or\
        ((ret.month == today.month) and\
        (ret.day > today.day)):
            return None
    return ret


def get_ssid():
    """
    Returns the currently connected SSID
    """
    command = "".join([
        "System/Library/PrivateFrameworks/Apple80211.framework/Versions/",
        "Current/Resources/airport -I",
    ])
    airport = shell_out(command)
    for i in airport:
        if re.match(r'^SSID:', i.strip()):
            return i.strip().strip("SSID: ")


def get_default_gateway_ip():
    """
    Returns the IP address of the currently connected gateway
    """
    netstat = shell_out("netstat -nr")
    for i in netstat:
        if i.startswith("default"):
            return filter(None, i.split(' '))[1]


def get_default_gateway_mac():
    """
    Returns the MAC address of the currently connected gateway
    """
    ip_addr = get_default_gateway_ip()
    arp = shell_out("arp -an")
    for i in arp:
        if ("(%s)" % ip_addr) in i:
            return i.split(' ')[3]


def is_mac_addr(mac):
    """
    Returns true if the inputted var is a propper MAC address, false
    if it's not
    """
    if type(mac) != 'str':
        return False
    if re.match(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', mac, re.IGNORECASE):
        return True
    else:
        return False


def ssh_length():
    """
    Returns an array of times that open ssh connections have been open
    """
    ssh_times = []
    ps_ax = shell_out("ps -ax -o etime,command -c")
    for i in ps_ax:
        data = i.strip().strip('\n').split(' ')
        if len(data) == 2 and data[-1] == 'ssh':
            ssh_times.append(data[0])
    return ssh_times


def scutil_dns():
    """
    Returns a dictinoary with the search domain, nameserver0 and nameserver1
    """
    scutil_command = shell_out("scutil --dns")
    scutil = {}
    if scutil_command:
        for i in scutil_command:
            j = filter(None, i.split(" "))
            if 'domain[0]' in j:
                scutil['search_domain'] = j[-1]
                continue
            elif 'nameserver[0]' in j:
                scutil['nameserver0'] = j[-1]
                continue
            elif 'nameserver[1]' in j:
                scutil['nameserver1'] = j[-1]
                continue
    return scutil
