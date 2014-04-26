#!/usr/bin/env python
"""
This is a set of helper functions for filesystem utilities
"""

from os import listdir, walk, stat
from os.path import isfile, isdir, join, getmtime, islink
from itertools import product
from hashlib import sha1
from stat import ST_MODE
from sys import getsizeof
from base64 import b64decode
from re import match
from operator import itemgetter

from system import shell_out


def list_all_in_dir(directory):
    """
    Returns an array of all files and dirs that are present in a directory.

    Arguments:
      - dir: the directory to be searched

    """
    try:
        if not directory.endswith('/'):
            directory = "%s/" % (directory, )
    except AttributeError:
        return []
    except OSError:
        return []
    return [directory + f for f in listdir(directory)]


def list_files_in_dir(directory):
    """
    Returns an array of files that are present in a directory. Note that this
    will not display any subdirectories that are present in the directory

    Arguments:
      - dir: the directory to be searched

    """
    try:
        if not directory.endswith('/'):
            directory = "%s/" % (directory, )
    except AttributeError:
        return []
    except OSError:
        return []
    return [directory + f for f in listdir(directory)\
            if isfile(join(directory, f))]


def list_dirs_in_dir(directory):
    """
    Returns an array of directories that are present in a directory.

    Arguments:
      - dir: the directory to be searched

    """
    try:
        if not directory.endswith('/'):
            directory = "%s/" % (directory, )
    except AttributeError:
        return []
    except OSError:
        return []
    return [directory + f for f in listdir(directory)\
            if isdir(join(directory, f))]


def get_most_recently_updated_file(directory):
    """
    Returns the path of the most recently updated file in a directory
    """
    try:
        files = list_files_in_dir(directory)
    except OSError:
        return None
    if files:
        try:
            return max(filter(lambda e: not islink(e), files), key=getmtime)
        except OSError:
            return None
    else:
        return None


def hash_file(filename):
    """
    Return the SHA1 hash of the supplied file

    Arguments:
      - filename: the file to be hashed
    """
    return sha1(file(filename, 'r').read()).hexdigest()


def get_executables():
    """
    Find all executable files on the system with mdfind
    """
    return shell_out("mdfind kMDItemContentType==public.unix-executable")


def get_documents():
    """
    Find all document files on the system with mdfind
    """
    files = []
    file_extensions = [
        "docx", "doc",
        "xlsx", "xls",
        "pptx", "ppt",
        "pdf",
        "key",
        "pages",
        "numbers"
    ]
    for ext in file_extensions:
        arg = "kMDItemDisplayName == *.%s" % (ext, )
        files += shell_out("mdfind %s" % (arg, ))
    return filter(None, files)


def hash_kext(kextfind, kext):
    """
    Looks in /System/Library/Extensions/ for a supplied kext and returns it's
    hash if it exists, None if it doesn't
    """
    kext = kext.split(".")[-1]
    found = None
    for i in kextfind:
        if i.split('/')[-1].strip('.kext') == kext:
            path = join(i, "Contents", "MacOS", kext)
            if isfile(path):
                found = path
                break
    else:
        ext_root = join('/System', 'Library', 'Extensions')

        path = join(ext_root,
                    "%s.kext" % (kext, ),
                    'Contents', 'MacOS',
                    kext)

        if isfile(path):
            return hash_file(path)

        path = join(ext_root,
                    "Apple%s.kext" % (kext, ),
                    'Contents', 'MacOS',
                    "Apple%s" % (kext, ))

        if isfile(path):
            return hash_file(path)

        path = join(ext_root, "%s.kext" % (kext, ), kext)

        if isfile(path):
            return hash_file(path)

        path = join('/System', 'Library', 'Filesystems', 'AppleShare',
                     "%s.kext" % (kext, ),
                     'Contents', 'MacOS',
                     kext)

        if isfile(path):
            return hash_file(path)

    if found is None:
        return found
    else:
        return hash_file(found)


def list_home_dirs():
    """
    Returns an array of all directories in /Users
    """
    return list_dirs_in_dir("/Users/")


def get_environment_files():
    """
    Returns an array of all potential environment files on the system
    """
    files = [
        ".MacOS/environment",
    ]
    env = []
    for i in product(list_home_dirs(), files):
        env.append("/".join(i))
    return env


def list_recentitems():
    """
    Returns an array of all com.apple.recentitems files
    """
    files = ["Library/Preferences/com.apple.recentitems.plist"]
    items = []
    for i in product(list_home_dirs(), files):
        if isfile("/".join(i)):
            items.append("/".join(i))
    return items


def find_with_perms(directory, perms):
    """
    Returns an array of all files and directories in a given directory
    that have given permissions

    Arguments:
      - dir: the directory to search
      - perms: the permissions to filter by (in regex form)
    """
    files = []
    for [i, _, _] in walk(directory):
        if match(r"%s" % (perms, ), oct(stat(i)[ST_MODE])[-3:]):
            files.append(i)
        for fname in list_files_in_dir(i):
            if match(r"%s" % (perms, ), oct(stat(i)[ST_MODE])[-3:]):
                files.append(fname)
    return files


def list_authorized_keys():
    """
    Returns an array of all authorized_keys files on the filesystem
    """
    files = [
        ".ssh/authorized_keys",
        ".ssh2/authorized_keys",
    ]

    keys = []
    for i in product(["/var/root/"], files):
        if isfile("/".join(i)):
            keys.append("/".join(i))
    for i in product(list_home_dirs(), files):
        if isfile("/".join(i)):
            keys.append("/".join(i))
    return keys


def list_ssh_keys(no_password=False):
    """
    Returns a list of all ssh keys on a system

    Arguments:
      - no_password: only return keys without a password. defaults to false,
        which returns all keys
    """
    files = [
        ".ssh/id_rsa",
    ]

    ssh_keys = []
    for i in product(list_home_dirs(), files):
        if isfile("/".join(i)):
            ssh_keys.append("/".join(i))
    if not no_password:
        return ssh_keys
    else:
        no_passphrase = []
        for key_file in ssh_keys:
            passphrase = False
            with open(key_file) as fname:
                for line in fname:
                    if "ENCRYPTED" in line:
                        passphrase = True
                        break
                if not passphrase:
                    no_passphrase.append(key_file)
        return no_passphrase


def list_weak_keys():
    """
    Returns an array of all authorized_keys file that contain the public keys
    to weak weak private keys

    Currently, this function looks for keys that
    - Are DSA keys (maximum of 1024 bit key length)
    - Are RSA keys with a hash that has a length of < 300 bytes
      2048 bit RSA keys have a public key hash size that are in between 315 and
      319 bytes
    """
    weak_keys = []
    for i in list_authorized_keys():
        try:
            with open(i) as fname:
                for line in fname:
                    alg = line.split(' ')[0]
                    key = line.split(' ')[1]
                    if alg == "ssh-rsa" and getsizeof(b64decode(key)) < 300:
                        weak_keys.append(i)
                    elif alg == "ssh-dss":
                        weak_keys.append(i)
        except IOError:
            pass
    return weak_keys


def list_current_host_pref_files():
    """
    Return an array of the files that are present in
    ~/Library/Prefernces/ByHost
    """
    files = []
    for home_dir in list_home_dirs():
        try:
            files += list_files_in_dir(
                home_dir + "/Library/Preferences/ByHost/"
            )
        except OSError:
            pass

    return files


def list_launch_agents():
    """
    Return an array of the files that are present in ~/Library/LaunchAgents,
    /System/Library/LaunchAgents/ and /Library/LaunchAgents/
    """
    files = list_system_launch_agents()
    files += list_library_launch_agents()
    files += list_homedir_launch_agents()
    return files


def list_system_launch_agents():
    """
    Return an array of the files that are present in
    /System/Library/LaunchAgents/
    """
    return list_files_in_dir("/System/Library/LaunchAgents/")


def list_library_launch_agents():
    """
    Return an array of the files that are present in /Library/LaunchAgents/
    """
    return list_files_in_dir("/Library/LaunchAgents/")


def list_homedir_launch_agents():
    """
    Return an array of the files that are present in ~/Library/LaunchAgents
    """
    files = []
    for home_dir in list_home_dirs():
        try:
            files += list_files_in_dir(home_dir + "/Library/LaunchAgents/")
        except OSError:
            pass

    return files


def list_launch_daemons():
    """
    Return an array of the files that are present in /Library/LaunchDaemons/
    and /System/Library/LaunchDaemons/
    """
    files = list_files_in_dir("/Library/LaunchDaemons/")
    files += list_files_in_dir("/System/Library/LaunchDaemons/")

    return files


def list_startup_items():
    """
    Return an array of files that are present in /Library/StartupItems/ and
    /System/Library/StartupItems/
    """
    files = list_all_in_dir("/Library/StartupItems/")
    files += list_all_in_dir("/System/Library/StartupItems/")

    return files


def list_scripting_additions():
    """
    Return an array of files that are present in /Library/ScriptingAdditions/
    """
    return list_files_in_dir("/Library/ScriptingAdditions")


def list_app_info_plist():
    """
    Returns an array of Info.plist files in the /Applications directory
    """
    applications = list_dirs_in_dir("/Applications")
    info = []
    if applications:
        for app in applications:
            filename = join(app, 'Contents', 'Info.plist')
            if isfile(filename):
                info.append(filename)
    return info


def list_plugin_info_plist():
    """
    Returns an array of Info.plist files in the /Library/Internet Plugins/
    directory
    """
    plugins = list_dirs_in_dir("/Library/Internet Plug-Ins")
    info = []
    if plugins:
        for plugin in plugins:
            filename = join(plugin, 'Contents', 'Info.plist')
            if isfile(filename):
                info.append(filename)
    return info


def is_ssh_key(filename):
    """
    Returns True if a file might be an ssh key, False if not
    """
    if isfile(filename) and getsizeof(filename) < 10000:
        with open(filename, 'rb') as key:
            line1 = next(key)
            return match("^[-]*BEGIN.*PRIVATE KEY[-]*$", line1) is not None
    else:
        return False


def find_ssh_keys():
    """
    Returns an array of SSH private keys on the host
    """
    keys = []
    keys1 = shell_out("mdfind kMDItemFSName=='id_*sa'")
    if keys1:
        for key in keys1:
            if key and not match("^/Users/[a-zA-Z0-9]*/.ssh", key):
                keys.append(key)

    keys2 = shell_out("mdfind kMDItemFSName=='*.id'")
    if keys2:
        for key in keys2:
            try:
                if isfile(key) and is_ssh_key(key):
                    keys.append(key)
            except OSError:
                pass
            except Exception:
                pass

    return keys
