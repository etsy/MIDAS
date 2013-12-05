#!/usr/bin/env python
"""
This is the config for MIDAS
"""
from os.path import dirname, realpath


class Config():
    """the main config class"""

    def __init__(self):
        pass

    config = {}

    current_dir = dirname(realpath(__file__))
    if "/Users" in current_dir:
        config['database'] = 'midas_hids.sqlite'
    else:
        config['database'] = '/tmp/midas_hids.sqlite'

    config['plist_check_keys'] = [
        'RunAtLoad',
        'WatchPaths',
        'KeepAlive',
        'StartInterval',
        'StartOnMount',
        'OnDemand',
        'QueueDirectories',
        'StandardInPath',
        'StandardOutPath',
        'StandardErrorPath',
        'Debug',
        'LaunchOnlyOnce',
        'Sockets',
        'OSAXHandlers',
        'LSEnvironment',
        'CFBundleVersion',
    ]

    config['plist_check_keys_hash'] = [
        'Program',
        'ProgramArguments'
    ]

    config['firewall_keys'] = [
        'allowsignedenabled',
        'firewallunload',
        'globalstate',
        'loggingenabled',
        'previousonstate',
        'stealthenabled',
        'version',
    ]

    @staticmethod
    def get(key, config=config):
        """simple get method for Config class"""
        try:
            return config[key]
        except KeyError:
            return None

    @staticmethod
    def exists(key, config=config):
        """simple exists method for Config class"""
        if key in config.keys():
            return True
        else:
            return False
