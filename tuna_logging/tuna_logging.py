#!/usr/bin/env python3

"""Tuna_logging docstring
Logging module for Tuna, using ZeroMQ for message passing.
"""

# 0MQ stub

import zmq
zmq_context = zmq.Context ( )

# definitions

def main ( ):
    # config logging module
    import logging
    logging.basicConfig ( filename = '/home/nix/tuna.log', level = logging.DEBUG )
    logging.info ( "Tuna logging module started." )
    logging.debug ( "Logging threshold: logging DEBUG or higher." )
    # instantiate a REP node 
    zmq_socket = zmq_context.socket ( zmq.REP )
    zmq_socket.bind ( "tcp://*:5000" )
    # log incoming messages
    while True:
        msg = zmq_socket.recv ( )
        logging.debug ( "%s" % msg.decode("utf-8") )
        zmq_socket.send ( b'ACK' )

class tuna_log_client:
    def __init__ ( self ):
        self.zmq_context = zmq.Context ( )
        self.zmq_socket = self.zmq_context.socket ( zmq.REQ )
        self.zmq_socket.connect ( "tcp://127.0.0.1:5000" )

    def log ( self, msg ):
        self.zmq_socket.send ( msg )
        answer = self.zmq_socket.recv ( )
        if answer.decode("utf-8") != 'ACK':
            print ( u'Something is fishy!' )
            print ( u'Received: "%s".' % answer.decode("utf-8") )
            print ( u"Expected: 'ACK'" )

# control

if __name__ == "__main__":
    main ( )
