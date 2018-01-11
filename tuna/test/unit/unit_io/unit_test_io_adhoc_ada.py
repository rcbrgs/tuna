import logging
import os
import tuna
import unittest

class unit_test_io_adhoc_ada(unittest.TestCase):
    def setUp(self):
        self.here = os.getcwd()
        self.home = os.path.expanduser("~")
        tuna.log.set_path(self.home + "/nose.log")

    def test_empty_file(self):
        tuna.io.read(self.here + "/tuna/test/unit/unit_io/fake_adhoc.ada")

    def test_no_file_name(self):
        ad = tuna.io.Ada()
        ad.read()

    def test_nonexisting_file(self):
        flag = False
        nonexisting_file_number = 0       
        file_name = ""
        
        while not flag:
            nonexisting_file_number += 1            
            file_name = 'adhoc_test_file_' + str(nonexisting_file_number) +'.adt'
            try:
                open(file_name, 'r')
            except OSError:
                flag = True
        
        # Unless a race condition, adhoc_test_file_?.ad2 does not exist.
        self.assertRaises(OSError, tuna.io.read, file_name)

    def test_valid_adt_file(self):
        log = logging.getLogger(__name__)
        g093 = tuna.io.read(self.here + "/tuna/test/unit/unit_io/G093/G093.ADT")
        tuna.io.write(file_name = "g093_fits.fits",
                      array = g093.array,
                      metadata = g093.metadata,
                      file_format = 'fits')
        g093_fits = tuna.io.read("g093_fits.fits")
        # since we read this file, which is costly, let's test the metadata.
        self.assertTrue('QUEENSGA' in g093_fits.metadata.keys())
        log.info(g093_fits.metadata.keys())
        self.assertTrue(g093_fits.metadata['QUEENSGA'][0][: 17] == \
                        '-359, -359, -339,' )
        log.info(g093_fits.metadata['QUEENSGA'][0][: 17])
        os.remove("g093_fits.fits")
        os.remove("metadata_g093_fits.fits")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
