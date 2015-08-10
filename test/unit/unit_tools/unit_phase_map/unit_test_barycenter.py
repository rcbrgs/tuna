import logging
import numpy
import os
import tuna
import unittest

class unit_test_barycenter_detector ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "nose.log" )

    def test_barycenter_creation ( self ):
        raw = tuna.io.read ( "test/unit/unit_io/partial_4_planes.fits" )
        #barycenter_detector = tuna.tools.phase_map.barycenter_detector ( raw )
        #barycenter_detector.join ( )
        #self.assertEqual ( int ( barycenter_detector.result.array [ 0 ] [ 0 ] ), 3 )
        pass

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
