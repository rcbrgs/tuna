"""
backend.py

This program is a wrapper, meant to allow Tuna to be used in the Python interpreter or inside Python console programs.
"""

import logging
import sys
import threading
import tuna
from tuna.zeromq.zmq_proxy import zmq_proxy

class zmq_daemon ( threading.Thread ):
    def __init__ ( self ):
        super ( zmq_daemon, self ).__init__ ( )
        self.daemon = True
        self.log = logging.getLogger ( __name__ )
        self.zmq_proxy_instance = zmq_proxy ( )

    def run ( self ):
        self.zmq_proxy_instance.run ( )

class backend ( object ):
    def __init__ ( self ):
        super ( backend, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )

        self.lock = False

    def start ( self ):
        self.log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                                     sys._getframe ( ).f_code.co_varnames ) )

        if self.lock == False:
            self.lock = True

            self.zmq_proxy_instance = zmq_daemon ( )
            self.zmq_proxy_instance.start ( )
