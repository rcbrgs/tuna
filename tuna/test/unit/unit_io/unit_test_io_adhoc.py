__version__ = "0.1.1"
__changelog = {
    "0.1.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP 257 compliance."},
    "0.1.0": {"Tuna": "0.13.0", "Change": "Updated test_wrong_dimension to use "\
              "newly protected method _discover_adhoc_type of tuna.io.adhoc."}
}

import logging
import os
import tuna
import unittest

class unit_test_io_adhoc(unittest.TestCase):
    def setUp(self):
        self.here = os.getcwd()
        self.home = os.path.expanduser("~")
        tuna.log.set_path(self.home + "/nose.log")
        self.log = logging.getLogger(__name__)
        self.log.error("here = {}".format(self.here))

    def test_empty_file(self):
        tuna.io.read(self.here + "/tuna/test/unit/unit_io/fake_adhoc.ad2")

    def test_no_file_name(self):
        ad = tuna.io.Adhoc()
        ad.read()

    def test_nonexisting_file(self):
        flag = False
        nonexisting_file_number = 0       
        file_name = ""
        
        while not flag:
            nonexisting_file_number += 1            
            file_name = 'adhoc_test_file_' + str(nonexisting_file_number) +'.ad2'
            try:
                open(file_name, 'r')
            except OSError:
                flag = True
        
        # Unless a race condition, adhoc_test_file_?.ad2 does not exist.
        self.assertRaises(OSError, tuna.io.read, file_name)

    def test_valid_2d_file ( self ):
        tuna.io.read(self.here + "/tuna/test/unit/unit_io/adhoc.ad2")

    def test_valid_3d_file ( self ):
        tuna.io.read(self.here + "/tuna/test/unit/unit_io/adhoc.ad3")

    def test_wrong_dimenson ( self ):
        ad = tuna.io.Adhoc(file_name = self.here \
                           + "/tuna/test/unit/unit_io/adhoc.ad3")
        ad._discover_adhoc_type()
        self.assertRaises(ValueError, ad._read_adhoc_2d)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
