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


class AnalyzePlist(object):
    """AnalyzePlist analyzes property list files installed on the system"""

    def __init__(self):
        self.data = {}
        self.pre_changed_files = []
        self.post_changed_files = []
        self.pre_new_files = []
        self.post_new_files = []
        self.check_keys = Config.get("plist_check_keys")
        self.check_keys_hash = Config.get("plist_check_keys_hash")
        self.hashes = self.gather_hashes()
        self.files = list_launch_agents() + list_launch_daemons() + \
            list_app_info_plist() + list_plugin_info_plist() + \
            list_current_host_pref_files()
        self.changed_files, self.new_files, \
        self.same_files = self.bucket_files(
            self.files,
            self.hashes,
        )
        self.plist_name = None
        self.plist_file = None

        if self.changed_files:
            self.analyze_changed_files()

        if self.new_files:
            self.analyze_new_files()

    def gather_hashes(self):
        """
        return a dictionary of plist names and their corresponding hashes
        """
        hash_data = ORM.select("plist", ["name", "hash"])
        hash_dict = {}
        if hash_data:
            for i in hash_data:
                hash_dict[i['name']] = i['hash']
        return hash_dict

    def bucket_files(self, files, hashes):
        """
        takes an array of files and a dictionary in {file: hash} form and
        returns data structures indicitive of which files have changed since
        the last execution
        """
        # changed files and new_files are dicts so that we can store the hash
        # when we compute and thus not have to compute it twice
        changed_files = {}
        new_files = {}

        # since the hash of same_files hasn't changed, we don't need to store
        # it past the comparison
        same_files = []

        for fname in files:
            file_hash = hash_file(fname)
            if fname in hashes:
                if hashes[fname] == file_hash:
                    same_files.append(fname)
                else:
                    changed_files[fname] = file_hash
            else:
                new_files[fname] = file_hash

        return changed_files, new_files, same_files

    def check_key(self, key):
        """
        Log the values of the launch agent/daemon keys in self.check_keys
        """
        value = get_plist_key(self.plist_file, key)
        if value:
            self.data[key.lower()] = str(to_ascii(value))
        else:
            self.data[key.lower()] = "KEY DNE"

    def check_key_executable(self, key):
        """
        Log the values of the launch agent/daemon keys in self.check_keys_hash
        """
        key = key.lower()
        key_hash = "%s_hash" % (key.lower(), )

        value = get_plist_key(self.plist_file, key)
        if value:
            try:
                if isinstance(value, basestring):
                    # This should only get triggered by the Program key
                    self.data[key] = str(to_ascii(value))
                    self.data[key_hash] = hash_file(str(to_ascii(value)))
                elif isinstance(value, (list, tuple)):
                    # This should only get triggered by the
                    # ProgramArguments key
                    self.data[key] = encode(" ".join(value))
                    self.data[key_hash] = hash_file(str(value[0]))
            except IOError:
                self.data[key_hash] = "File DNE"
        else:
            self.data[key] = "KEY DNE"
            self.data[key_hash] = "KEY DNE"

    def analyze_changed_files(self):
        """
        analyze plists that have changed since last execution
        """
        where_params = self.changed_files.keys()
        where_statement = "name=%s" % (" OR name=".join(
            ['?'] * len(where_params)), )
        where_clause = [where_statement, where_params]
        self.pre_changed_files = ORM.select("plist", None, where_clause)
        for fname, fname_hash in self.changed_files.iteritems():
            self.data = {}
            self.plist_name = fname
            self.plist_file = read_plist(fname)
            self.data["name"] = self.plist_name
            self.data["date"] = exec_date
            self.data["hash"] = fname_hash

            for i in self.check_keys_hash:
                self.check_key_executable(i)
            for i in self.check_keys:
                self.check_key(i)

            # Aggregate self.data
            self.post_changed_files.append(self.data)

    def analyze_new_files(self):
        """
        analyze new plists that are on the host
        """
        where_params = self.new_files.keys()
        where_statement = "name=%s" % (" OR name=".join(
            ['?'] * len(where_params)), )
        where_clause = [where_statement, where_params]
        self.pre_new_files = ORM.select("plist", None, where_clause)
        self.post_new_files = []
        for fname, fname_hash in self.new_files.iteritems():
            self.data = {}
            self.plist_name = fname
            self.plist_file = read_plist(fname)
            self.data["name"] = self.plist_name
            self.data["date"] = exec_date
            self.data["hash"] = fname_hash

            for i in self.check_keys_hash:
                self.check_key_executable(i)
            for i in self.check_keys:
                self.check_key(i)

            # Aggregate self.data
            self.post_new_files.append(self.data)


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


@run_every_60
class AnalyzeFirewallKeys(object):
    """
    AnalyzeFirewallKeys analyzes the top level keys of com.apple.alf.plist
    """

    def __init__(self):
        self.data = []

    def check_firewall_keys(self):
        """
        Checks the top level keys of com.apple.alf.plist
        """
        alf = read_plist('/Library/Preferences/com.apple.alf.plist')
        if alf:
            for i in Config.get("firewall_keys"):
                key = str(get_plist_key(alf, i))
                if key:
                    self.data.append({
                        "name": i,
                        "date": exec_date,
                        "value": key
                    })

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_firewall_keys()


@run_every_60
class AnalyzeFirewallExceptions(object):
    """Analyzes the systems firewall exceptions"""

    def __init__(self):
        self.data = []

    def check_firewall_exceptions(self):
        """
        Checks the systems firewall exceptions
        """
        alf = read_plist('/Library/Preferences/com.apple.alf.plist')
        if alf:
            exceptions = get_plist_key(alf, "exceptions")
            if exceptions:
                for i in exceptions:
                    try:
                        self.data.append({
                            "name": i['path'],
                            "date": exec_date,
                            "state": str(i['state'])
                        })
                    except OSError:
                        pass
                    except Exception:
                        pass

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_firewall_exceptions()


@run_every_60
class AnalyzeFirewallExplicitauths(object):
    """Analyzes the firewall's explicit auth"""

    def __init__(self):
        self.data = []

    def check_firewall_explicitauths(self):
        """
        Checks the systems firewall explicitauths
        """
        alf = read_plist('/Library/Preferences/com.apple.alf.plist')
        if alf:
            explicitauths = get_plist_key(alf, "explicitauths")
            if explicitauths:
                for i in explicitauths:
                    try:
                        self.data.append({"name": i['id'], "date": exec_date})
                    except OSError:
                        pass
                    except Exception:
                        pass

    def analyze(self):
        """
        This is the 'main' method that launches all of the other checks
        """
        self.check_firewall_explicitauths()


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
        a = AnalyzePlist()
        if a is not None:
            plist_pre_changed_files = a.pre_changed_files
            plist_post_changed_files = a.post_changed_files
            plist_pre_new_files = a.pre_new_files
            plist_post_new_files = a.post_new_files

            data_science = DataScience(
                ORM,
                plist_post_changed_files,
                "plist",
                "name",
                plist_pre_changed_files,
            )
            data_science.get_changed_entries()

            data_science = DataScience(
                ORM,
                plist_post_new_files,
                "plist",
                "name",
                plist_pre_new_files,
            )
            data_science.get_new_entries()
    except Exception, error:
        print error_running_file(__file__, "lad", error)

    try:
        a = AnalyzeKexts()
        if a is not None:
            a.analyze()
            kext_data = a.data

            data_science = DataScience(ORM, kext_data, "kexts")
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__, "analyze_kexts", error)

    try:
        a = AnalyzeFirewallKeys()
        if a is not None:
            a.analyze()
            firewall_keys_data = a.data

            data_science = DataScience(
                ORM,
                firewall_keys_data,
                "firewall_keys"
            )
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__, "analyze_firewall_keys", error)

    try:
        a = AnalyzeFirewallExceptions()
        if a is not None:
            a.analyze()
            firewall_exceptions_data = a.data

            data_science = DataScience(
                ORM,
                firewall_exceptions_data,
                "firewall_exceptions"
            )
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__,
                                 "analyze_firewall_exceptions",
                                 error)

    try:
        a = AnalyzeFirewallExplicitauths()
        if a is not None:
            a.analyze()
            firewall_explicitauths_data = a.data

            data_science = DataScience(
                ORM,
                firewall_explicitauths_data,
                "firewall_explicitauths"
            )
            data_science.get_all()
    except Exception, error:
        print error_running_file(__file__,
                                 "analyze_firewall_explicit_auths",
                                 error)

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
