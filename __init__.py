
"""
Tuna

This program provides access to Tuna's libraries' namespaces.
"""

import tuna.console
import tuna.data_cube
import tuna.io
import tuna.gui
import tuna.log
import tuna.tools
import tuna.zeromq

class daemons ( object ):
    def __init__ ( self ):
        super ( daemons, self ).__init__ ( )
        self.tuna_daemons = console.backend ( )
        self.tuna_daemons.start ( )

o_daemons = daemons ( )
