import logging
import tuna
import unittest

class unit_test_io_adhoc ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "nose.log" )

    def test_empty_file ( self ):
        tuna.io.read ( "test/unit/unit_io/fake_adhoc.ad2" )

    def test_no_file_name ( self ):
        ad = tuna.io.adhoc ( )
        ad.read ( )

    def test_nonexisting_file ( self ):
        flag = False
        nonexisting_file_number = 0       
        file_name = ""
        
        while not flag:
            nonexisting_file_number += 1            
            file_name = 'adhoc_test_file_' + str ( nonexisting_file_number ) + '.ad2'
            try:
                open ( file_name, 'r' )
            except OSError:
                flag = True
        
        # Unless a race condition, adhoc_test_file_?.ad2 does not exist.
        self.assertRaises ( OSError, tuna.io.read, file_name )

    def test_valid_2d_file ( self ):
        tuna.io.read ( "test/unit/unit_io/adhoc.ad2" )

    def test_valid_3d_file ( self ):
        tuna.io.read ( "test/unit/unit_io/adhoc.ad3" )

    def test_wrong_dimenson ( self ):
        ad = tuna.io.adhoc ( file_name = "test/unit/unit_io/adhoc.ad3" )
        ad.discover_adhoc_type ( )
        self.assertRaises ( ValueError, ad.read_adhoc_2d )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
