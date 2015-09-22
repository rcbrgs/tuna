"""
This module defines classes useful for running as background processes when Tuna is used.
"""

import logging
import sys
import threading
import tuna
from tuna.zeromq.zmq_proxy import zmq_proxy

class zmq_daemon ( threading.Thread ):
    """
    This class encapsulates a ZeroMQ proxy running as an independent thread.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.
    """
    def __init__ ( self ):
        super ( zmq_daemon, self ).__init__ ( )
        self.daemon = True
        self.log = logging.getLogger ( __name__ )
        self.zmq_proxy_instance = zmq_proxy ( )

    def run ( self ):
        self.zmq_proxy_instance.run ( )

class backend ( object ):
    """
    This class wraps calls for all necessary background processes for Tuna.
    """
    def __init__ ( self ):
        super ( backend, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.lock = False

    def start ( self ):
        self.log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                                     sys._getframe ( ).f_code.co_varnames ) )

        if self.lock == False:
            self.lock = True

            self.zmq_proxy_instance = zmq_daemon ( )
            self.zmq_proxy_instance.start ( )

            self.db = tuna.io.database ( )
            self.db.start ( )
