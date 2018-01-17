"""This module's scope covers background processes.
"""
__version__ = "0.2.1"
__changelog = {
    "0.2.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.2.0": {"Tuna": "0.14.0", "Change": "improved docstrings."},
    "0.1.0": {"Change": "Initial changelog version."}
}

import logging
import sys
import threading
import tuna
from tuna.zeromq.zmq_proxy import ZMQProxy

class Backend(object):
    """This class' responsability is to wrap calls for all necessary background 
    processes for Tuna.
    """
    def __init__(self):
        super(Backend, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        self.lock = False

    def start ( self ):
        """This method will launch the ZeroMQ proxy instance and the database on
        the first time it is called. Subsequent calls are ignored.        

        Example::

            b = tuna.console.Backend ( )
            b.start ( )
        """
        self.log.debug("%s %s" % (sys._getframe().f_code.co_name,
                                  sys._getframe().f_code.co_varnames))

        if not self.lock:
            self.lock = True

            self.zmq_proxy_instance = ZMQDaemon()
            self.zmq_proxy_instance.start()

            self.db = tuna.io.Database()
            self.db.start()

class ZMQDaemon(threading.Thread):
    """This class encapsulates a ZeroMQ proxy running as an independent thread.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts
    its thread execution. Clients are expected to use its .join ( ) method 
    before using its results.

    This class is not intended for public use, and therefore its signature is 
    not exposed by default.

    Example::

        from tuna.console.Backend import *
        tz = tuna.console.Backend.ZMQDaemon ( )
        tz.start ( )
    """
    def __init__(self):
        super(ZMQDaemon, self ).__init__()
        self.log = logging.getLogger(__name__)
        self.zmq_proxy_instance = ZMQProxy()

        self.daemon = True

    def run(self):
        """This method is called when the thread object's start ( ) method is 
        called. 
        It will call this object's ZeroMQ proxy instance's run ( ) method.

        Example::

            from tuna.console.Backend import *
            tz = tuna.console.Backend.ZMQDaemon ( )
            tz.start ( )
        """
        self.zmq_proxy_instance.run()
