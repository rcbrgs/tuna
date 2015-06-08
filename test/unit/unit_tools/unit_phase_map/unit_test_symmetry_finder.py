import logging
import numpy
import os
import tuna
import unittest

class unit_test_symmetry_center_finder ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "../nose.log" )

    def test_barycenter_creation ( self ):
        raw = tuna.io.read ( "test/unit/unit_io/adhoc.ad3" )
        barycenter_detector = tuna.tools.phase_map.barycenter_fast ( raw )
        barycenter_detector.join ( )
        wrapped = barycenter_detector.result
        center = tuna.tools.phase_map.find_image_center_by_symmetry ( data = wrapped.array )
        self.assertTrue ( center [ 0 ] > 250 )
        self.assertTrue ( center [ 0 ] < 270 )
        self.assertTrue ( center [ 1 ] > 210 )
        self.assertTrue ( center [ 1 ] < 230 )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
