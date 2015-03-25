
"""
Tuna

This program provides access to Tuna's libraries' namespaces.
"""

from .console        import console
from .data_cube      import data_cube
from .io             import io
from .io.convenience import read, write
from .gui            import gui
from .log            import log
from .tools          import tools
from .zeromq         import zeromq

class daemons ( object ):
    def __init__ ( self ):
        super ( daemons, self ).__init__ ( )
        self.tuna_daemons = console.backend ( )
        self.tuna_daemons.start ( )

o_daemons = daemons ( )
