"""Tuna
====

Tuna is a data "reduction" solution for Fabry-Pérot interferometer data,
specially for astrophysics applications.

As of version v0.11.0 of Tuna, the scope of reduction that is processed covers
the transformation of raw interferometer data into wavelength-calibrated data.

Tuna is highly modular, and its modules are organized in trees of namespaces and
modules, where each non-terminalnode is a namespace and leafs are modules.

Subpackages
-----------

console
    Modules related to background processes of Tuna.
io
    Wrappers for file formats typical in astrophysics (FITS, ADHOC) and the Tuna
    .can file format, which is a Python pickle containing a numpy array with
    image data and a Python dictionary with the metadata.
log
    Contains modules for creating and handling log destinations. Uses Python's
    logging module.
models
    Models relevant for synthesizing and fitting Fabry-Pérot data.
pipelines
    Recipes tieing together Tuna's tools and framework to attain some "standard"
    reduction goal.
plugins
    Tuna's modular system allow for parts of its pipelines to be changed, either
    by rewriting the code or by calling external executables. This is done
    through the plugin system.
repo
    Modules for remote access to files.
test
    Code for the testing of Tuna, using Python's unittest and nose.
tools
    Modules with individual tasks, and modules with pre-designed pipelines for
    data reduction pipelines that use the tasks.
zeromq
    Hub and client for accessing and processing data remotely.

Numpy indexing order
--------------------

From Tuna v0.11.0 onwards, we are adopting the convention mentioned in:
http://docs.scipy.org/doc/numpy/reference/internals.html, so that rows will be
the last item indexed. Therefore, cubes in tuna should be indexed as [ planes,
columns, rows ].
"""
__version__ = "0.10.8"
__changelog = {
    "0.10.8": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.10.7": {"Tuna": "0.15.0", "Change": "pipelines, plugins namespaces."},
    "0.10.6": {"Tuna": "0.14.0", "Change": "improved documentation."},
    "0.10.5": {"Change": "Docstring."},
    "0.10.4": {"Change": "Added db link through the daemons."},
    "0.10.3": {"Change": "Even less spammy."},
    "0.10.2": {"Change": "Tweaked logging to be less spammy for user."},
    "0.10.1": {"Change": "Refactored the logging facility to have more stdout " \
               "information, and at the same time save info to log file if " \
               "specified."}
}

import logging
import sys

import tuna.console
import tuna.io
from tuna.io.convenience import (read,
                                 write)
import tuna.log
import tuna.models
import tuna.pipelines
import tuna.tools
import tuna.plugins
import tuna.zeromq

import tuna.generator
from tuna.generator.adhocfile import *

class Daemons (object):
    """This class allows to create a wrapper object for the console.backend class.
    """
    def __init__(self):
        super(Daemons, self).__init__()
        self.tuna_daemons = console.Backend()
        self.tuna_daemons.start()

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
_log_handlers = []
_log_handlers.append(handler)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(message)s",
                              datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
_log.addHandler(handler)

_daemons = Daemons()
db = _daemons.tuna_daemons.db
