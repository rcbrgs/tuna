import threading
import tuna
import unittest
import zmq

class ThreadedBus(threading.Thread):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.zmq_bus_instance = tuna.zeromq.ZMQProxy()

    def close(self):
        self.zmq_bus_instance.close()

    def run(self):
        self.zmq_bus_instance.run()

class unit_test_zmq_client(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_zmq_bus_replies(self):
        return 

        self.threaded_bus_instance = ThreadedBus()
        self.threaded_bus_instance.start()

        client = tuna.zeromq.ZMQClient()
        answer = client.send("test")
        self.assertEqual(answer, 'ACK')
        
        self.threaded_bus_instance.close()
        self.threaded_bus_instance.join()
        
    def test_zmq_bus_requests(self):
        pass

    def test_zmq_bus_forwards(self):
        pass

if __name__ == '__main__':
    unittest.main()
