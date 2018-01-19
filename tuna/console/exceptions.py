"""This module's scope covers exceptions.
"""
__version__ = '0.1.2'
__changelog = {
    "0.1.2": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.1": {"Change": "Improved docstring to conventional style."},
    "0.1.0": {"Change": "tabs to spaces to mimic better ipython's traceback."}
}

import inspect
import sys
import traceback

def output_exception(error):
    """This method's goal is: to print information about the error raised as 
    exception.

    Parameters:

    error : exception
        A valid Python exception, such as one caught in a try / except loop.

    Returns:

    message : string
        A string containing the error string and its traceback, similar to 
        IPython's output when an exception occurs.

    Example::

        try:
            tuna.io.read("non existing file name.fits")
        except Excetion as e:
            tuna.console.exceptions.output_exception(e)
    """
    
    callee = inspect.stack()[1][0].f_code.co_name
    exception_info = sys.exc_info()
    message = "{} detected exception {}. From sys.exc_info(), its type is {}, "\
              + "value is {} and its traceback is: {}".format(
        callee, error, exception_info[0], exception_info[1], exception_info[2])
    tracebacks = traceback.extract_tb(exception_info[2])
    for entry in tracebacks:
        message += "\n  File '{}', line {}, in {}\n    {}".format(
            entry[0], entry[1], entry[2], entry[3])
    return message
