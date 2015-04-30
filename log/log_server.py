"""
Tuna logging server.

Classes:
log_server -- Daemon that saves to file messages received through ZeroMQ.
"""

import logging
import os
import time
import tuna
import zmq

class log_server ( object ):
    """
    Log incoming messages.
    """

    def __init__ ( self ):
        super ( log_server, self ).__init__ ( )
        self.logger = logging.getLogger ( "tuna_logger" )
        self.logger.setLevel ( logging.DEBUG )
        self.logger_handler = None
        self.logger_formatter = None

        log_path = "."
        if 'TUNA_PATH' in os.environ.keys ( ):
            log_path = os.environ [ 'TUNA_PATH' ]
        self.set_path ( log_path + "/tuna.log" )

        time_string = time.strftime ( "%Y-%m-%d %H:%M:%S " )
        self.logger.debug ( time_string + "Tuna (debug): Logging module started." )
        time_string = time.strftime ( "%Y-%m-%d %H:%M:%S " )
        self.logger.info  ( time_string + "Tuna  (info): Logging threshold: logging DEBUG or higher." )
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

        time_string = time.strftime ( "%Y-%m-%d %H:%M:%S " )

        # logging levels are:
        # CRITICAL 50
        # ERROR    40
        # WARNING  30
        # INFO     20
        # DEBUG    10
        if ( type == "debug" ): 
            self.logger.debug   ( time_string + "Tuna (debug): " + contents )
        elif ( type == "info" ):
            self.logger.info    ( time_string + "Tuna  (info): " + contents )
        elif ( type == "warning" ):
            self.logger.warning ( time_string + "Tuna  (warn): " + contents )
        elif ( type == "error" ):
            self.logger.error ( time_string + "Tuna (error): " + contents )
        elif ( type == "critical" ):
            self.logger.critical ( time_string + "Tuna  (crit): " + contents )
        else:
            self.logger.debug   ( time_string + "Tuna     (?): " + contents )

    def run ( self ):
        started = False
        first_try = True
        while ( not started ):
            try: 
                started = True
                self.__zmq_socket_rep.bind ( "tcp://127.0.0.1:5001" )
            except zmq.ZMQError as error_message:
                if ( first_try ):
                    #print ( "ZMQError: %s." % str ( error_message ) )
                    #print ( "Is log_server already running? Will silently retry every 10 seconds." )
                    first_try = False
                started = False
                time.sleep ( 10 )

        while self._keep_running == True:
            zmq_buffer = dict ( self.__zmq_poller.poll ( 5000 ) )
            if self.__zmq_socket_rep in zmq_buffer and zmq_buffer [ self.__zmq_socket_rep ] == zmq.POLLIN:
                msg = self.__zmq_socket_rep.recv ( )
                self.parse ( msg )
                self.__zmq_socket_rep.send ( b'ACK' )

    def set_path ( self,
                   log_file_name ):
        format_string = "%(message)s"
        if self.logger.hasHandlers ( ):
            for handler in self.logger.handlers:
                self.logger.removeHandler ( handler )
        self.logger_handler = logging.FileHandler ( log_file_name )
        self.logger_formatter = logging.Formatter ( )
        self.logger_handler.setFormatter ( self.logger_formatter )
        self.logger.addHandler ( self.logger_handler )

    def __del__ ( self ):
        self._keep_running = False

def main ( ):
    tuna_log_server = log_server ( )
    tuna_log_server.run ( )
    
if __name__ == "__main__":
    main ( )

def get_logger ( ):
    return tuna.o_daemons.tuna_daemons.log_server_instance.log_server_instance

def set_path ( log_file_path ):
    tuna.o_daemons.tuna_daemons.log_server_instance.log_server_instance.set_path ( log_file_path )
