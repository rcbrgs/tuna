import unittest

class unit_test_zmq_bus ( unittest.TestCase ):
    def setUp ( self ):
        import threading
        class threaded_bus ( threading.Thread ):
            def __init__ ( self ):
                #super ( threaded_bus, self ).__init ( )
                threading.Thread.__init__ ( self )
                import sys
                sys.path.append ( '/home/nix/sync/tuna' )
                from github.zmq import zmq_bus
                self.zmq_bus_instance = zmq_bus.zmq_bus ( )
            def close ( self ):
                self.zmq_bus_instance.close ( )
            def run ( self ):
                self.zmq_bus_instance.run ( )
        self.threaded_bus_instance = threaded_bus ( )
        self.threaded_bus_instance.start ( )
        import zmq
        self.zmq_context = zmq.Context ( )
        self.zmq_socket_req = self.zmq_context.socket ( zmq.REQ )
        self.zmq_socket_req.connect ( "tcp://127.0.0.1:5000" )

    def test_zmq_bus_replies ( self ):
        self.zmq_socket_req.send ( b'test: replies ok' )
        answer = self.zmq_socket_req.recv ( )
        self.assertEqual ( answer, b'ACK' )

#    def test_zmq_bus_requests ( self ):
#        pass

#    def test_zmq_bus_forwards ( self ):
#        pass

    def tearDown ( self ):
        self.threaded_bus_instance.close ( )
        self.threaded_bus_instance.join ( )

if __name__ == '__main__':
    unittest.main ( )
