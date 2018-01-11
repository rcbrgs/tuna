import logging
import numpy
import os
import tuna
import unittest

class unit_test_arc_segmentation_center_finder(unittest.TestCase):
    def setUp(self):
        self.here = os.getcwd()
        self.home = os.path.expanduser("~")
        tuna.log.set_path(self.home + "/nose.log")

    def test_center_finder(self):
        wrapped = tuna.io.read(
            self.here + "/tuna/test/unit/unit_io/G094_03_wrapped_phase_map.fits")
        noise = tuna.io.read(
            self.here + "/tuna/test/unit/unit_io/G094_04_noise.fits")
        center_finder = tuna.tools.phase_map.arc_segmentation_center_finder(
            wrapped, noise)
        center_finder.join()
        
        self.assertTrue(center_finder.center[0] > 190)
        self.assertTrue(center_finder.center[0] < 250)
        self.assertTrue(center_finder.center[1] > 220)
        self.assertTrue(center_finder.center[1] < 280)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
