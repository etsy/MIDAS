#!/usr/bin/env python
"""
This is the declaration file for a set of useful decorators. The "DRY" rule is
intentionally violated here in an effort to provide nice syntactic sugar
"""

from time import strftime, gmtime, time


def run_every_5(func):
    """
    a decorator for running functions every 5 minutes
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        minute = int(strftime("%M", gmtime()))
        ret = None
        if minute % 5 == 0:
            ret = func(*args, **kwargs)
        return ret
    return decorated


def run_every_10(func):
    """
    a decorator for running functions every 10 minutes
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        minute = int(strftime("%M", gmtime()))
        ret = None
        if minute % 10 == 0:
            ret = func(*args, **kwargs)
        return ret
    return decorated


def run_every_15(func):
    """
    a decorator for running functions every 15 minutes
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        minute = int(strftime("%M", gmtime()))
        ret = None
        if minute % 15 == 0:
            ret = func(*args, **kwargs)
        return ret
    return decorated


def run_every_20(func):
    """
    a decorator for running functions every 20 minutes
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        minute = int(strftime("%M", gmtime()))
        ret = None
        if minute % 20 == 0:
            ret = func(*args, **kwargs)
        return ret
    return decorated


def run_every_30(func):
    """
    a decorator for running functions every 30 minutes
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        minute = int(strftime("%M", gmtime()))
        ret = None
        if minute % 30 == 0:
            ret = func(*args, **kwargs)
        return ret
    return decorated


def run_every_60(func):
    """
    a decorator for running functions every 60 minutes
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        minute = int(strftime("%M", gmtime()))
        ret = None
        if minute == 0:
            ret = func(*args, **kwargs)
        return ret
    return decorated


def timer(func):
    """
    a decorator for timing code execution
    """
    def decorated(*args, **kwargs):
        """
        internal decorator method
        """
        start = time()
        ret = func(*args, **kwargs)
        end = time()
        print "ty_name=perf function=\"%s\" time=\"%.4f\"" % (
            func.__name__,
            end - start,
        )
        return ret
    return decorated
