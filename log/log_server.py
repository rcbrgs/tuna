"""
Tuna logging server.

Classes:
log_server -- Daemon that saves to file messages received through ZeroMQ.
"""

import logging
from os.path import expanduser
import time
import zmq

class log_server ( object ):
    """
    Log incoming messages.
    """

    def __init__ ( self ):
        super ( log_server, self ).__init__ ( )
        # config logging module
        log_file_name = expanduser ( "~/tuna.log" )
        format_string = "%(asctime)-15s %(message)s"
        logging.basicConfig ( filename = log_file_name, 
                              format = format_string, 
                              level = logging.DEBUG )
        logging.debug ( "Tuna (debug): Logging module started." )
        logging.info  ( "Tuna  (info): Logging threshold: logging DEBUG or higher." )
        # instantiate a REP node 
        self.__zmq_context = zmq.Context ( )
        self.__zmq_socket_rep = self.__zmq_context.socket ( zmq.REP )
        self.__zmq_poller = zmq.Poller ( )
        self.__zmq_poller.register ( self.__zmq_socket_rep, zmq.POLLIN )

        self._keep_running = True

    def parse ( self, 
                msg = str ):
        decoded = msg.decode ( "utf-8" )
        split = decoded.partition ( ": " )
        if len ( split [2] ) == 0:
            type = "?"
            contents = split [ 0 ]
        else:
            type = split [ 0 ].lower ( )
            contents = split [ 2 ]
        # logging levels are:
        # CRITICAL 50
        # ERROR    40
        # WARNING  30
        # INFO     20
        # DEBUG    10
        if ( type == "debug" ): 
            logging.debug   ( "Tuna (debug): " + contents )
        elif ( type == "info" ):
            logging.info    ( "Tuna  (info): " + contents )
        elif ( type == "warning" ):
            logging.warning ( "Tuna  (warn): " + contents )
        elif ( type == "error" ):
            logging.warning ( "Tuna (error): " + contents )
        elif ( type == "critical" ):
            logging.warning ( "Tuna  (crit): " + contents )
        else:
            logging.debug   ( "Tuna     (?): " + contents )
        
    def run ( self ):
        started = False
        first_try = True
        while ( not started ):
            try: 
                started = True
                self.__zmq_socket_rep.bind ( "tcp://127.0.0.1:5001" )
            except zmq.ZMQError as error_message:
                if ( first_try ):
                    print ( "ZMQError: %s." % str ( error_message ) )
                    print ( "Is log_server already running? Will silently retry every 10 seconds." )
                    first_try = False
                started = False
                time.sleep ( 10 )

        while self._keep_running == True:
            zmq_buffer = dict ( self.__zmq_poller.poll ( 5000 ) )
            if self.__zmq_socket_rep in zmq_buffer and zmq_buffer [ self.__zmq_socket_rep ] == zmq.POLLIN:
                msg = self.__zmq_socket_rep.recv ( )
                self.parse ( msg )
                self.__zmq_socket_rep.send ( b'ACK' )

    def __del__ ( self ):
        self._keep_running = False

def main ( ):
    tuna_log_server = log_server ( )
    tuna_log_server.run ( )
    
if __name__ == "__main__":
    main ( )
