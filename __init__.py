# coding: latin-1
"""
Tuna
====

Is a data reduction solution for Fabry-Perot interferometer data, specially for astrophysics applications.

Subpackages
-----------

io
    Wrappers for file formats typical in astrophysics (FITS, ADHOC) and the Tuna can file format, which is a Python pickle containing the numpy array with data and a dictionary with the metadata.
models
    Models relevant for synthesizing and fitting Fabry-Pérot data.
tools
    Modules with individual tasks, and modules with pre-designed pipelines for data reduction pipelines that use the tasks.
zeromq
    Hub and client for accessing and processing data remotely.

Indexing order
--------------

From Tuna v0.11 onwards, we are adopting the convention mentioned in: http://docs.scipy.org/doc/numpy/reference/internals.html, so that rows will be the last item indexed. Therefore, cubes in tuna should be indexed as [ planes, columns, rows ].
"""

__version__ = '0.10.1'
changelog = {
    '0.10.1'  : "Refactored the logging facility to have more stdout information, and at the same time save info to log file if specified."
    }

import logging
import sys

import tuna.console
import tuna.io
from tuna.io.convenience import ( read,
                                  write )
import tuna.log
import tuna.models
import tuna.tools
import tuna.zeromq

class daemons ( object ):
    def __init__ ( self ):
        super ( daemons, self ).__init__ ( )
        self.tuna_daemons = console.backend ( )
        self.tuna_daemons.start ( )

_log = logging.getLogger ( __name__ )
_log.setLevel ( logging.INFO )

handler = logging.StreamHandler ( stream = sys.stdout )
_log_handlers = [ ]
_log_handlers.append ( handler )
handler.setLevel ( logging.DEBUG )
formatter = logging.Formatter ( fmt = "%(asctime)s %(levelname)5s %(message)s", 
                                datefmt = '%Y-%m-%d %H:%M:%S' )
handler.setFormatter ( formatter )
_log.addHandler ( handler )

__daemons = daemons ( )
