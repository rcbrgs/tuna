"""
Tuna's ZeroMQ proxy module.

Its main responsibility is to forward messages, be it to other Tuna modules, or to external services.

Classes:
zmq_bus -- (stub) zmq proxy
"""

import time
import zmq

class zmq_proxy ( ):
    """
    (stub) zmq proxy: sets zmq context, binds to port 5000, and orchestrates tuna messages.

    Public methods:
    run -- enters the orchestration loop.
    """

    def __init__ ( self ):
        self.__zmq_context = zmq.Context ( )
        self.__zmq_socket_rep = self.__zmq_context.socket ( zmq.REP )

        self.__lock = False
        self.__zmq_poller = zmq.Poller ( )
        self.__zmq_poller.register ( self.__zmq_socket_rep, zmq.POLLIN )


    def __call_log ( self, msg ):
        """
        Dispatch msg to log server.
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
        Print received message.
        """
        print ( "zmq_proxy received the message '%s'." % msg )


    def check_ACK ( self, ack_msg ):
        if ack_msg.decode ( "utf-8" ) != 'ACK':
            print ( u'Something is fishy!' )
            print ( u'Received: "%s" from %s.' % answer.decode("utf-8"), msg_destination )
            print ( u"Expected: 'ACK'" )

    def close ( self ):
        print ( "Shutting down zmq_proxy." )
        self.__lock = False

    def __del__ ( self ):
        """
        Gracefully shutdown this process.
        """

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
        Orchestrate incoming messages.

        This method will run in loop, listening to messages and dispatching them as appropriated.

        destination_call_table is a dictionary associating target strings with the functions to be run. The services responsible for a given target can be changed here without changing the clients.
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

def main ( ):
    standalone_zmq_proxy = zmq_proxy ( )
    standalone_zmq_proxy.run ( )

if __name__ == "__main__":
    main ( )
