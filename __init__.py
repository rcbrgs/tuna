
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
import tuna.tools
import tuna.zeromq

class daemons ( object ):
    def __init__ ( self ):
        super ( daemons, self ).__init__ ( )
        self.tuna_daemons = console.backend ( )
        self.tuna_daemons.start ( )

__tuna_logger = logging.getLogger ( __name__ )
__tuna_logger.setLevel ( logging.DEBUG )

__daemons = daemons ( )

