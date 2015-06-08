import logging
import numpy
import os
import tuna
import unittest

class unit_test_barycenter_detector ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "../nose.log" )

    def test_barycenter_creation ( self ):
        raw = tuna.io.read ( "test/unit/unit_io/adhoc.ad3" )
        barycenter_detector = tuna.tools.phase_map.barycenter_fast ( raw )
        barycenter_detector.join ( )
        self.assertEqual ( int ( barycenter_detector.result.array [ 0 ] [ 0 ] ), 27 )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
