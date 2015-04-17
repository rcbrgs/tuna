"""
Tuna's ZeroMQ client module.

Classes:
zmq_client -- zmq client that uses (stub) proxy for communication.
Utilizing the lazy pirate pattern from 0MQ documentation.
"""

import zmq

class zmq_client ( ):
    """
    Sets zmq context, connects to (stub) proxy and sends messages.

    Public methods:
    log -- sends message to logging server.
    """

    def __init__ ( self ):
        self.zmq_context = zmq.Context ( )
        
    def close_socket ( self ):
        self.zmq_socket_req.setsockopt ( zmq.LINGER, 0 )
        self.zmq_socket_req.close ( )
        self.poller.unregister ( self.zmq_socket_req )

    def log ( self, msg ):
        """
        Sends (byte string) message to log_server through the (stub) proxy.
        """
        self.open_socket ( )
        self.register_poller ( )

        prefixed_msg = "log: " + msg

        self.zmq_socket_req.send_unicode ( prefixed_msg )
        
        retries = 0
        unanswered = True
        while unanswered:
            answer = dict ( self.poller.poll ( 1000 ) )
            if answer.get ( self.zmq_socket_req ) == zmq.POLLIN:
                answer = self.zmq_socket_req.recv ( )
                if answer.decode("utf-8") != 'ACK':
                    print ( u'Something is fishy!' )
                    print ( u'Received: "%s".' % answer.decode("utf-8") )
                    print ( u"Expected: 'ACK'" )
                unanswered = False
            else:
                retries += 1
                self.open_socket ( )
                self.register_poller ( )
                suffixed_message = prefixed_msg + " (message resent " + str ( retries ) + " times)" 
                self.zmq_socket_req.send_unicode ( suffixed_message )

        self.close_socket ( )

    def open_socket ( self ):
        self.zmq_socket_req = self.zmq_context.socket ( zmq.REQ )
        self.zmq_socket_req.connect ( "tcp://127.0.0.1:5000" )

    def register_poller ( self ):
        self.poller = zmq.Poller ( )
        self.poller.register ( self.zmq_socket_req,
                               zmq.POLLIN )


def main ( ):
    pass

if __name__ == "__main__":
    main ( )
