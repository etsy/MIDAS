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
from lib.helpers.utilities import error_running_file
from lib.tables.example import tables
from lib.decorators import run_every_60

@run_every_60
class AnalyzeFirewallProcesses(object):
    """Analyzes the firewalled processes in the system firewall"""

    def __init__(self):
        self.data = []

    def check_firewall_processes(self):
        """
        Checks the firewalled processes in the system firewall
        """
        alf = read_plist('/Library/Preferences/com.apple.alf.plist')
        if alf:
            processes = get_plist_key(alf, "firewall")
            if processes:
                for key, value in processes.iteritems():
                    try:
                        name = key
                        state = str(value['state'])
                        process = value['proc']
                        try:
                            servicebundleid = value['servicebundleid']
                        except KeyError:
                            servicebundleid = "KEY DNE"
                        self.data.append({
                            "name": name,
                            "date": exec_date,
                            "state": state,
                            "process": process,
                            "servicebundleid": servicebundleid
                        })
                    except KeyError:
                        pass
                    except Exception:
                        pass

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_firewall_processes()


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
        a = AnalyzeFirewallProcesses()
        if a is not None:
            a.analyze()
            firewall_processes_data = a.data

            data_science = DataScience(
                ORM,
                firewall_processes_data,
                "firewall_processes"
            )
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__, "analyze_firewall_processes", error)

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Execution took %s seconds.", str(end - start))
