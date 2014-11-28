"""
Tuna's ZeroMQ bus module.

Classes:
zmq_bus -- (stub) zmq proxy
"""

import zmq

class zmq_bus ( ):
    """
    (stub) zmq proxy: sets zmq context, binds to port 5000, and orchestrates tuna messages.

    Public methods:
    run -- enters the orchestration loop.
    """

    def __init__ ( ):
        self.__zmq_context = zmq.Context ( )
        self.__zmq_socket_req = self.__zmq_context.socket ( zmq.REQ )
        self.__zmq_socket_rep = self.__zmq_context.socket ( zmq.REP )
        self.__zmq_socket_rep.bind ( "tcp://127.0.0.1:5000" )


    def run ( ):
        """
        Orchestrate incoming messages.

        This method will run in loop, listening to messages and dispatching them as appropriated.
        """

        while True:
            msg = self.__zmq_socket_rep.recv ( )
            msg_partition = msg.partition ( ": " )
            msg_destination = msg_partition[0]
            if msg_destination == 'log':
                self.__zmq_socket_req.connect ( "tcp://127.0.0.1:5001" )
                self.__zmq_socket_req.send ( "%s" % msg_partition[2].decode("utf-8") )
                answer = self.__zmq_socket_req.recv ( ) 
                if answer.decode ( "utf-8" ) != 'ACK':
                    print ( u'Something is fishy!' )
                    print ( u'Received: "%s" from %s.' % answer.decode("utf-8"), msg_destination )
                    print ( u"Expected: 'ACK'" )
                self.__zmq_socket_rep.send ( b'ACK' )


def main ( ):
    zmq_proxy = zmq_bus ( )
    zmq_proxy.run ( )

if __name__ == "__main__":
    main ( )
