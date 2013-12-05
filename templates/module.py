#!/usr/bin/env python
"""
This is a template MIDAS module.
"""

from time import time
from sys import argv
import logging


def analyze_something():
    """
    Use a function to do the heavy work of the analysis, check or verification
    """
    pass

class AnalyzeSomethingComplex():
    """Template class for analyzing something complex"""

    def __init__(self):
        """
        If the check requires a lot of related tasks that are better
        abstracted out into several functions, make a class
        """
        var = self.helper_function_1()
        if var:
            for each in var:
                self.helper_function_2(each)

    def helper_function_1(self):
        """
        Don't forget to write docstrings for every function!
        """
        return []

    def helper_function_2(self, each):
        """
        Don't forget to write docstrings for every function!
        """
        pass

if __name__ == "__main__":

    start = time()

    try:
        analyze_something()
        AnalyzeSomethingComplex()
    except Exception, error:
        print "ty_error_running_file=%s ty_error_message=\"%s\"" % (
            __file__,
            repr(error),
        )

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Execution took %s seconds." % str(end-start))
