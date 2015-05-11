
"""
Tuna

This program provides access to Tuna's libraries' namespaces.
"""

import logging

import tuna.console
import tuna.io
from tuna.io.convenience import ( read,
                                  write )
import tuna.gui
import tuna.log
import tuna.tools
import tuna.zeromq

class daemons ( object ):
    def __init__ ( self ):
        super ( daemons, self ).__init__ ( )
        self.tuna_daemons = console.backend ( )
        self.tuna_daemons.start ( )

_log = logging.getLogger ( __name__ )
_log.setLevel ( logging.DEBUG )
_log_handler = None
_log_formatter = None

__daemons = daemons ( )
