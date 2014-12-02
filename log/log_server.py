"""
Logging server for Tuna

This server runs as a daemon and saves to file messages received through ZeroMQ from Tuna.
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



def main ( ):
    # config logging module
    logging.basicConfig ( filename = '/home/nix/tuna.log', level = logging.DEBUG )
    logging.info ( "Tuna logging module started." )
    logging.debug ( "Logging threshold: logging DEBUG or higher." )
    # instantiate a REP node 
    zmq_context = zmq.Context ( )
    zmq_socket = zmq_context.socket ( zmq.REP )
    zmq_socket.bind ( "tcp://127.0.0.1:5001" )
    # log incoming messages
    while True:
        msg = zmq_socket.recv ( )
        logging.debug ( "%s" % msg.decode("utf-8") )
        zmq_socket.send ( b'ACK' )


# control

if __name__ == "__main__":
    main ( )
