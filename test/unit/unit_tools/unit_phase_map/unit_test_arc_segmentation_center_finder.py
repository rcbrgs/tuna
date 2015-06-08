import logging
import numpy
import os
import tuna
import unittest

class unit_test_arc_segmentation_center_finder ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "../nose.log" )

    def test_center_finder ( self ):
        raw = tuna.io.read ( "test/unit/unit_io/adhoc.ad3" )
        barycenter_detector = tuna.tools.phase_map.barycenter_fast ( raw )
        barycenter_detector.join ( )
        wrapped = barycenter_detector.result
        noise_detector = tuna.tools.phase_map.noise_detector ( raw,
                                                               wrapped,
                                                               1 )
        noise_detector.join ( )
        noise = noise_detector.noise
        center_finder = tuna.tools.phase_map.arc_segmentation_center_finder ( wrapped,
                                                                              noise )
        center_finder.join ( )
        
        self.assertTrue ( center_finder.center [ 0 ] > 110 )
        self.assertTrue ( center_finder.center [ 0 ] < 130 )
        self.assertTrue ( center_finder.center [ 1 ] > 450 )
        self.assertTrue ( center_finder.center [ 1 ] < 470 )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
