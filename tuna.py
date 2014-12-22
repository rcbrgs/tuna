"""
Tuna

This script is a wrapper around the essential modules of Tuna, and will start the necessary processes to run a graphical client.

Once the client is closed, the other modules will be shutdown also.
"""

from gui import simple_gui
from log import log_server
from PyQt4.QtGui import QApplication
import sys
import threading
from zeromq import zmq_proxy

class zmq_daemon ( threading.Thread ):
    def __init__ ( self ):
        super ( zmq_daemon, self ).__init__ ( )
        self.zmq_proxy_instance = zmq_proxy.zmq_proxy ( )

    def close ( self ):
        self.zmq_proxy_instance.close ( )

    def run ( self ):
        self.zmq_proxy_instance.run ( )

class log_daemon ( threading.Thread ):
    def __init__ ( self ):
        super ( log_daemon, self ).__init__ ( ) 
        self.log_server_instance = log_server.log_server ( )        

    def run ( self ):
        self.log_server_instance.run ( )

    def close ( self ):
        self.log_server_instance.close ( )

class gui_daemon ( threading.Thread ):
    def __init__ ( self, log_instance = None ):
        super ( gui_daemon, self ).__init__ ( )
        self.__log_instance = log_instance

    def run ( self ):
        app = QApplication ( sys.argv )
        simple_gui_instance = simple_gui.simple_gui ( desktop_widget = app.desktop ( ) )
        sys.exit ( app.exec_ ( ) )

if __name__ == '__main__':
    zmq_proxy_instance = zmq_daemon ( )
    log_server_instance = log_daemon ( )
    gui_instance = gui_daemon ( log_server_instance.log_server_instance )

    zmq_proxy_instance.start ( )
    log_server_instance.start ( )

    gui_instance.start ( )
    gui_instance.join ( )

    log_server_instance.close ( )
    zmq_proxy_instance.close ( )
