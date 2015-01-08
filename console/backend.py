"""
backend.py

This program is a wrapper, meant to allow Tuna to be used in the Python interpreter or inside Python console programs.
"""

import sys
import threading
import tuna

class zmq_daemon ( threading.Thread ):
    def __init__ ( self ):
        super ( zmq_daemon, self ).__init__ ( )
        self.zmq_proxy_instance = tuna.zeromq.zmq_proxy ( )

    def close ( self ):
        self.zmq_proxy_instance.close ( )

    def run ( self ):
        self.zmq_proxy_instance.run ( )

class log_daemon ( threading.Thread ):
    def __init__ ( self ):
        super ( log_daemon, self ).__init__ ( ) 
        self.log_server_instance = tuna.log.log_server ( )        

    def run ( self ):
        self.log_server_instance.run ( )

    def close ( self ):
        self.log_server_instance.close ( )

class backend ( object ):
    def __init__ ( self ):
        super ( backend, self ).__init__ ( )
        self.lock = False

    def start ( self ):
        if self.lock == False:
            self.lock = True
            self.zmq_proxy_instance = zmq_daemon ( )
            self.log_server_instance = log_daemon ( )
            self.zmq_proxy_instance.start ( )
            self.log_server_instance.start ( )

    def finish ( self ):
        self.log_server_instance.close ( )
        self.zmq_proxy_instance.close ( )
        self.lock = False
