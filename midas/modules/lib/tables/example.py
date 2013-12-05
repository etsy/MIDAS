#!/usr/bin/env python
"""
This is an example table definition
"""

tables = {
    "plist" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "hash" : {
            "type" : "text",
            "default" : "NULL",
        },
        "program" : {
            "type" : "text",
            "default" : "NULL",
        },
        "program_hash" : {
            "type" : "text",
            "default" : "NULL",
        },
        "programarguments" : {
            "type" : "text",
            "default" : "NULL",
        },
        "programarguments_hash" : {
            "type" : "text",
            "default" : "NULL",
        },
        "runatload" : {
            "type" : "text",
            "default" : "NULL",
        },
        "watchpaths" : {
            "type" : "text",
            "default" : "NULL",
        },
        "keepalive" : {
            "type" : "text",
            "default" : "NULL",
        },
        "startinterval" : {
            "type" : "text",
            "default" : "NULL",
        },
        "startonmount" : {
            "type" : "text",
            "default" : "NULL",
        },
        "ondemand" : {
            "type" : "text",
            "default" : "NULL",
        },
        "queuedirectories" : {
            "type" : "text",
            "default" : "NULL",
        },
        "standardinpath" : {
            "type" : "text",
            "default" : "NULL",
        },
        "standardoutpath" : {
            "type" : "text",
            "default" : "NULL",
        },
        "standarderrorpath" : {
            "type" : "text",
            "default" : "NULL",
        },
        "debug" : {
            "type" : "text",
            "default" : "NULL",
        },
        "launchonlyonce" : {
            "type" : "text",
            "default" : "NULL",
        },
        "sockets" : {
            "type" : "text",
            "default" : "NULL",
        },
        "osaxhandlers" : {
            "type" : "text",
            "default" : "NULL",
        },
        "lsenvironment" : {
            "type" : "text",
            "default" : "NULL",
        },
        "cfbundleversion" : {
            "type" : "text",
            "default" : "NULL",
        },
    },
    "kexts" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "hash" : {
            "type" : "text",
            "default" : "NULL",
        },
    },
    "firewall_keys" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "value" : {
            "type" : "text",
            "default" : "NULL",
        },
    },
    "firewall_exceptions" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "state" : {
            "type" : "text",
            "default" : "NULL",
        },
    },
    "firewall_explicitauths" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
    },
    "firewall_processes" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "state" : {
            "type" : "text",
            "default" : "NULL",
        },
        "process" : {
            "type" : "text",
            "default" : "NULL",
        },
        "servicebundleid" : {
            "type" : "text",
            "default" : "NULL",
        },
    },
    "firewall_applications" : {
        "name" : {
            "type" : "text",
            "nullable" : False,
        },
        "date" : {
            "type" : "text",
            "nullable" : False,
        },
        "state" : {
            "type" : "text",
            "default" : "NULL",
        },
    },
}
