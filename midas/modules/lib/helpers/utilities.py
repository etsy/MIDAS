#!/usr/bin/env python
"""
This is a set of helper functions for general utilities
"""

import difflib


def diff(string1, string2):
    """
    Returns an array where array[0] is the content of s2 that have been added
    in regards to s1 and array[1] is the content of s2 that has been removed
    from s1
    """
    differ = difflib.Differ()
    added = ""
    removed = ""
    for i in differ.compare(string1, string2):
        if i[0] == "+":
            added += i[2]
        elif i[0] == "-":
            removed += i[2]
    return [added, removed]


def to_ascii(value):
    """
    Returns the ascii representation of a given string
    """
    if isinstance(value, basestring):
        try:
            return value.encode("ascii", "replace")
        except UnicodeError:
            return None
        except Exception:
            return None
    elif isinstance(value, dict):
        try:
            temp_dict = {}
            for i, j in value.iteritems():
                temp_dict[i] = to_ascii(j)
            return temp_dict
        except UnicodeError:
            return None
        except Exception:
            return None


def encode(string):
    """
    URL encodes single quotes and double quotes in an inputted string. This
    isn't done for any security reasons, it's just done so that splunk doesn't
    misinterpret key="value" strings
    """
    string = string.replace("'", "%27")
    string = string.replace('"', "%22")
    return string


def error_running_file(filename, section, error):
    """returns a string in log format if a module errors out"""
    file_error = "ty_error_running_file=%s" % (filename, )
    section_error = "ty_error_section=%s" % (section, )
    error_message = "ty_error_message=%r" % (error, )

    return " ".join([
        file_error,
        section_error,
        error_message,
    ])
