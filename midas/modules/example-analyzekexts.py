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




class AnalyzeKexts(object):
    """AnalyzeKexts analyzes and aggregates currently installed kernel
    extensions"""

    def __init__(self):
        self.data = []

    def check_kernel_extensions(self):
        """
        Log all loaded kernel extensions
        """
        kernel_extensions = get_kextstat()
        extension_paths = get_kextfind()
        for i in kernel_extensions.itervalues():
            try:
                file_hash = hash_kext(extension_paths, i['Name'])
                if not file_hash:
                    file_hash = "KEY DNE"
                self.data.append({
                    "name": i['Name'],
                    "date": exec_date,
                    "hash": file_hash
                })
            except KeyError:
                pass

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_kernel_extensions()


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
        a = AnalyzeKexts()
        if a is not None:
            a.analyze()
            kext_data = a.data

            data_science = DataScience(ORM, kext_data, "kexts")
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__, "analyze_kexts", error)

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Execution took %s seconds.", str(end - start))
