"""
Tuna logging server.

Classes:
log_server -- Daemon that saves to file messages received through ZeroMQ.
"""

import logging
from os.path import expanduser
import zmq

class log_server ( object ):
    """
    Log incoming messages.
    """

    def __init__ ( self ):
        super ( log_server, self ).__init__ ( )
        # config logging module
        log_file_name = expanduser ( "~/tuna.log" )
        s_format = "%(asctime)-15s %(message)s"
        logging.basicConfig ( filename = log_file_name, 
                              format = s_format, 
                              level = logging.DEBUG )
        logging.info ( "Tuna logging module started." )
        logging.debug ( "Logging threshold: logging DEBUG or higher." )
        # instantiate a REP node 
        self.__zmq_context = zmq.Context ( )
        self.__zmq_socket_rep = self.__zmq_context.socket ( zmq.REP )
        try: 
            self.__zmq_socket_rep.bind ( "tcp://127.0.0.1:5001" )
        except zmq.ZMQError as error_message:
            print ( "ZMQError: %e." % error_message )
            import sys
            sys.exit ( 'Tuna log server error: Could not bind to port.' )
        self.__zmq_poller = zmq.Poller ( )
        self.__zmq_poller.register ( self.__zmq_socket_rep, zmq.POLLIN )

        self._keep_running = True

    def parse ( self, 
                s_msg = str ):
        s_decoded = s_msg.decode ( "utf-8" )
        l_split = s_decoded.partition ( ": " )
        if len ( l_split [2] ) == 0:
            s_type = "info"
            s_contents = l_split [ 0 ]
        else:
            s_type = l_split [ 0 ].lower ( )
            s_contents = l_split [ 2 ]
        if ( s_type == "debug" ):
            logging.debug ( s_contents )
        elif ( s_type == "info" ):
            logging.info ( s_contents )
        else:
            logging.info ( s_contents )
        
    def run ( self ):
        while self._keep_running == True:
            zmq_buffer = dict ( self.__zmq_poller.poll ( 5000 ) )
            if self.__zmq_socket_rep in zmq_buffer and zmq_buffer [ self.__zmq_socket_rep ] == zmq.POLLIN:
                msg = self.__zmq_socket_rep.recv ( )
                #logging.debug ( "%s" % msg.decode("utf-8") )
                self.parse ( msg )
                self.__zmq_socket_rep.send ( b'ACK' )

    def close ( self ):
        self._keep_running = False

def main ( ):
    tuna_log_server = log_server ( )
    tuna_log_server.run ( )
    
if __name__ == "__main__":
    main ( )
