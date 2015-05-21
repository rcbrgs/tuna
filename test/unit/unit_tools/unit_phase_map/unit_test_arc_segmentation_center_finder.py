import logging
import numpy
import os
import tuna
import unittest

class unit_test_arc_segmentation_center_finder ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "../nose.log" )

    def test_barycenter_creation ( self ):
        raw = tuna.io.read ( "test/unit/unit_io/adhoc.ad3" )
        barycenter_detector = tuna.tools.phase_map.barycenter_detector ( raw )
        barycenter_detector.join ( )
        wrapped = barycenter_detector.result
        center_finder = tuna.tools.phase_map.arc_segmentation_center_finder ( wrapped )
        center_finder.join ( )
        self.assertTrue ( center_finder.center [ 0 ] > 120 )
        self.assertTrue ( center_finder.center [ 0 ] < 140 )
        self.assertTrue ( center_finder.center [ 1 ] > 450 )
        self.assertTrue ( center_finder.center [ 1 ] < 470 )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
