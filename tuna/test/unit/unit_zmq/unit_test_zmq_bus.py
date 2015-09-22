import threading
import tuna
import unittest
import zmq

class threaded_bus ( threading.Thread ):
    def __init__ ( self ):
        super ( threaded_bus, self ).__init__ ( )
        self.zmq_bus_instance = tuna.zeromq.zmq_proxy ( )

    def close ( self ):
        self.zmq_bus_instance.close ( )

    def run ( self ):
        self.zmq_bus_instance.run ( )

class unit_test_zmq_bus ( unittest.TestCase ):
    @classmethod
    def setUpClass ( self ):
        pass

    @classmethod
    def tearDownClass ( self ):
        pass

    def test_zmq_bus_replies ( self ):
        return 

        self.threaded_bus_instance = threaded_bus ( )
        self.threaded_bus_instance.start ( )

        self.zmq_context = zmq.Context ( )
        self.zmq_socket_req = self.zmq_context.socket ( zmq.REQ )
        self.zmq_socket_req.connect ( "tcp://127.0.0.1:5000" )
        self.zmq_socket_req.send ( b'test: zmq bus replies?' )
        answer = self.zmq_socket_req.recv ( )
        self.assertEqual ( answer, b'ACK' )

        self.threaded_bus_instance.close ( )
        self.threaded_bus_instance.join ( )
        
    def test_zmq_bus_requests ( self ):
        pass

    def test_zmq_bus_forwards ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
