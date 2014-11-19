#!/usr/bin/env python3

"""tuna_viewer_2d docstring
Basic viewer widget for 2d images. As standalone, minimal GUI for opening FITS files.
"""

import zmq

def main ( ):
    zmq_context = zmq.Context ( )
    zmq_socket = zmq_context.socket ( zmq.REQ )
    zmq_socket.connect ( "tcp://127.0.0.1:5000" )
    zmq_socket.send ( b'Hi' )
    zmq_ack = zmq_socket.recv ( )
    print ( zmq_ack )

if __name__ == "__main__":
    main ( )
