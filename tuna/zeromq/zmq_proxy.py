"""
This module's scope is: to mediate communication between ZeroMQ clients.
"""

import time
import zmq

class zmq_proxy ( ):
    """
    This class' responsibility is to setup a ZeroMQ proxy and mediate message passing between its clients.
    It binds to port 5000.
    """

    def __init__ ( self ):
        self.__zmq_context = zmq.Context ( )
        self.__zmq_socket_rep = self.__zmq_context.socket ( zmq.REP )

        self.__lock = False
        self.__zmq_poller = zmq.Poller ( )
        self.__zmq_poller.register ( self.__zmq_socket_rep, zmq.POLLIN )


    def __call_log ( self, msg ):
        """
        This method's goal is to dispatch the input message to a log server.

        Parameters:

        - msg, a string.
        """
        self.__zmq_socket_req = self.__zmq_context.socket ( zmq.REQ )
        self.__zmq_socket_req.setsockopt ( zmq.LINGER, 0 )
        self.__zmq_socket_req.connect ( "tcp://127.0.0.1:5001" )

        self.__zmq_socket_req.send ( msg.encode("utf-8") )
        answer = self.__zmq_socket_req.recv ( ) 
        if answer.decode ( "utf-8" ) != 'ACK':
            print ( u'Something is fishy!' )
            print ( u'Received: "%s" from %s.' % answer.decode("utf-8"), msg_destination )
            print ( u"Expected: 'ACK'" )

        self.__zmq_socket_req.close ( )

    def __call_print ( self, msg ):
        """
        This method's goal is to print a received message. It is meant as a fallback in case the log server is unavailable.
        """
        print ( "zmq_proxy received the message '%s'." % msg )


    def check_ACK ( self, ack_msg ):
        """
        This method's goal is to verify that the input ZeroMQ message contains the string "ACK".

        Parameters:

        - *ack_msg*, a byte string.
        """
        if ack_msg.decode ( "utf-8" ) != 'ACK':
            print ( u'Something is fishy!' )
            print ( u'Received: "%s" from %s.' % answer.decode("utf-8"), msg_destination )
            print ( u"Expected: 'ACK'" )

    def close ( self ):
        """
        This method's goal is to gracefully shutdown the ZeroMQ proxy.
        """
        print ( "Shutting down zmq_proxy." )
        self.__lock = False

    def __del__ ( self ):
        self.__lock = False

        self.__zmq_socket_req = self.__zmq_context.socket ( zmq.REQ )
        self.__zmq_socket_req.setsockopt ( zmq.LINGER, 0 )
        self.__zmq_socket_req.connect ( "tcp://127.0.0.1:5000" )

        self.__zmq_socket_req.send ( b'info: Shutting down zmq_proxy.' )
        answer = self.__zmq_socket_req.recv ( )
        self.check_ACK ( answer )

        self.__zmq_socket_req.close ( )

    def run ( self ):
        """
        This method's goal is to orchestrate incoming messages.
        It  will run in loop, listening to messages and dispatching them as appropriated.
        
        Note to developers: destination_call_table is a dictionary associating target strings with the functions to be run. The services responsible for a given target can be changed here without changing the clients.
        """

        started = False
        first_try = True
        while ( not started ):
            try: 
                started = True
                self.__zmq_socket_rep.bind ( "tcp://127.0.0.1:5000" )
            except zmq.ZMQError as error_message:
                if ( first_try ):
                    #print ( 'ZMQError: %s' % error_message )
                    #print ( "Is zmq_proxy already running? Will silently retry every 10 seconds." )
                    first_try = False
                time.sleep ( 10 )
                started = False
        self.__lock = True

        destination_call_table = {
            'info' : self.__call_print,
            'log'  : self.__call_log,
            'test' : self.__call_print, }

        while self.__lock == True:
            zmq_buffer = dict ( self.__zmq_poller.poll ( 5 ) )
            if self.__zmq_socket_rep in zmq_buffer and zmq_buffer [ self.__zmq_socket_rep ] == zmq.POLLIN:
                msg = self.__zmq_socket_rep.recv ( )
                msg_partition = str ( msg, ( "utf-8" ) ).partition ( ": " )
                msg_destination = msg_partition[0]
                msg_contents = msg_partition[2]
                destination_call_table [ msg_destination ] ( msg_contents )
                self.__zmq_socket_rep.send ( b'ACK' )

