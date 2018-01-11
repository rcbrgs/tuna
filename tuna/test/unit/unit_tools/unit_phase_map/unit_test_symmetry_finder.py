import logging
import numpy
import os
import tuna
import unittest

class unit_test_symmetry_center_finder(unittest.TestCase):
    def setUp(self):
        self.here = os.getcwd()
        self.home = os.path.expanduser("~")
        tuna.log.set_path(self.home + "/nose.log")

    def test_barycenter_creation(self):
        raw = tuna.io.read(self.here + "/tuna/test/unit/unit_io/adhoc.ad3")
        barycenter_detector = tuna.tools.barycenter.barycenter_fast(raw)
        barycenter_detector.join()
        wrapped = barycenter_detector.result
        center = tuna.tools.phase_map.find_image_center_by_symmetry(
            data = wrapped.array)
        self.assertTrue(center[1] > 250)
        self.assertTrue(center[1] < 270)
        self.assertTrue(center[0] > 210)
        self.assertTrue(center[0] < 230)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
