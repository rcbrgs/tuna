#!/usr/bin/env python3

"""Tuna_logging docstring
Logging module for Tuna, using ZeroMQ for message passing.
"""

import logging
import zmq

logging.basicConfig ( filename = '/home/nix/tuna.log', level = logging.DEBUG )

logging.info ( "Tuna logging module started." )
logging.debug ( "Logging threshold: logging DEBUG or higher." )

zmq_context = zmq.Context ( )

def main ( ):
    # instantiate a REP node 
    zmq_socket = zmq_context.socket ( zmq.REP )
    zmq_socket.bind ( "tcp://*:5000" )
    # log incoming messages
    while True:
        msg = zmq_socket.recv ( )
        logging.debug ( "%s", msg )
        zmq_socket.send ( b'ACK' )

if __name__ == "__main__":
    main ( )
