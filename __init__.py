"""
Tuna

This program provides access to Tuna's libraries' namespaces.

From Tuna v0.11 onwards, we are adopting the convention mentioned in: http://docs.scipy.org/doc/numpy/reference/internals.html, so that rows will be the last item indexed. Therefore, cubes in tuna should be indexed as [ planes, columns, rows ].
"""

__version__ = '0.10.0'

import logging

import tuna.console
import tuna.io
from tuna.io.convenience import ( read,
                                  write )
import tuna.log
import tuna.tools
import tuna.zeromq

class daemons ( object ):
    def __init__ ( self ):
        super ( daemons, self ).__init__ ( )
        self.tuna_daemons = console.backend ( )
        self.tuna_daemons.start ( )

_log = logging.getLogger ( __name__ )
_log.setLevel ( logging.INFO )
_log_handler = None
_log_formatter = None

__daemons = daemons ( )
