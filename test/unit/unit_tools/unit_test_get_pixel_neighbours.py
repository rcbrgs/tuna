import logging
import numpy
import os
import tuna
import unittest

class unit_test_get_pixel_neighbours ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "/home/nix/nose.log" )
        self.array = numpy.ones ( shape = ( 3, 3 ) )

    def test_normal_pixel ( self ):
        neighbours = tuna.tools.get_pixel_neighbours ( position = ( 1, 1 ),
                                                       array = self.array )

        self.assertEqual ( set ( neighbours ), set ( [ ( 0, 0 ), ( 0, 1 ), ( 0, 2 ),
                                                       ( 1, 0 ),           ( 1, 2 ),
                                                       ( 2, 0 ), ( 2, 1 ), ( 2, 2 ) ] ) )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
