#!/usr/bin/env python
"""
This is an example MIDAS module
"""

from os.path import isfile
from os import chmod
from time import time, gmtime, strftime
import logging
from sys import argv

from lib.ty_orm import TyORM
from lib.plist import read_plist, get_plist_key
from lib.config import Config
from lib.data_science import DataScience
from lib.helpers.filesystem import hash_file, list_launch_agents, \
    list_launch_daemons, list_app_info_plist, list_plugin_info_plist, \
    hash_kext, list_current_host_pref_files
from lib.helpers.system import get_kextstat, get_kextfind
from lib.helpers.utilities import to_ascii, encode, error_running_file
from lib.tables.example import tables
from lib.decorators import run_every_60



@run_every_60
class AnalyzeFirewallApplications(object):
    """Analyzes firewalled application state in the systems firewall"""

    def __init__(self):
        self.data = []

    def check_firewall_applications(self):
        """
        Checks firewalled application state in the systems firewall
        """
        alf = read_plist('/Library/Preferences/com.apple.alf.plist')
        if alf:
            applications = get_plist_key(alf, "applications")
            if applications:
                for i in applications:
                    try:
                        name = i['bundleid']
                        state = str(i['state'])
                    except KeyError:
                        continue
                    except Exception:
                        continue
                    self.data.append({
                        "name": name,
                        "date": exec_date,
                        "state": state
                    })

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_firewall_applications()

if __name__ == "__main__":

    start = time()

    # the "exec_date" is used as the "date" field in the datastore
    exec_date = strftime("%a, %d %b %Y %H:%M:%S", gmtime())

    # the table definitions are stored in a library file. this is instantiating
    # the ORM object and initializing the tables
    ORM = TyORM(Config.get("database"))
    if isfile(Config.get("database")):
        chmod(Config.get("database"), 0600)
    for k, v in tables.iteritems():
        ORM.initialize_table(k, v)

    ###########################################################################
    # Gather data
    ###########################################################################
    try:
        a = AnalyzeFirewallApplications()
        if a is not None:
            a.analyze()
            firewall_applications_data = a.data

            data_science = DataScience(
                ORM,
                firewall_applications_data,
                "firewall_applications"
            )
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__,
                                 "analyze_firewall_applications",
                                 error)

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Execution took %s seconds.", str(end - start))
