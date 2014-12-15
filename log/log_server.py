"""
Tuna logging server.

Classes:
log_server -- Daemon that saves to file messages received through ZeroMQ.
"""

import logging
import zmq

class log_server ( ):
    def __init__ ( self ):
        # config logging module
        logging.basicConfig ( filename = '/home/nix/tuna.log', level = logging.DEBUG )
        logging.info ( "Tuna logging module started." )
        logging.debug ( "Logging threshold: logging DEBUG or higher." )
        # instantiate a REP node 
        self.zmq_context = zmq.Context ( )
        self.zmq_socket_rep = self.zmq_context.socket ( zmq.REP )
        self.zmq_socket_rep.bind ( "tcp://127.0.0.1:5001" )
    def run ( self ):
        """
        Log incoming messages.
        """
        while True:
            msg = self.zmq_socket_rep.recv ( )
            logging.debug ( "%s" % msg.decode("utf-8") )
            self.zmq_socket_rep.send ( b'ACK' )

def main ( ):
    tuna_log_server = log_server ( )
    tuna_log_server.run ( )

if __name__ == "__main__":
    main ( )
