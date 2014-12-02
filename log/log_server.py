"""
Tuna logging server.

Classes:
log_server -- Daemon that saves to file messages received through ZeroMQ.
"""

import logging
import zmq

#class tuna_log_server:
#    def __init__ ( self ):
#        self.zmq_context = zmq.Context ( )
#        self.zmq_socket = self.zmq_context.socket ( zmq.REQ )
#        self.zmq_socket.connect ( "tcp://127.0.0.1:5000" )
#
#    def log ( self, msg ):
#        self.zmq_socket.send ( msg )
#        answer = self.zmq_socket.recv ( )
#        if answer.decode("utf-8") != 'ACK':
#            print ( u'Something is fishy!' )
#            print ( u'Received: "%s".' % answer.decode("utf-8") )
#            print ( u"Expected: 'ACK'" )


class log_server ( ):
    def __init__ ( self ):
        # config logging module
        logging.basicConfig ( filename = '/home/nix/tuna.log', level = logging.DEBUG )
        logging.info ( "Tuna logging module started." )
        logging.debug ( "Logging threshold: logging DEBUG or higher." )
        # instantiate a REP node 
        self.zmq_context = zmq.Context ( )
        self.zmq_socket_rep = zmq_context.socket ( zmq.REP )
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
