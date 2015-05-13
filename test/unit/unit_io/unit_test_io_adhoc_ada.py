import logging
import tuna
import unittest

class unit_test_io_adhoc ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "../nose.log" )

    def test_empty_file ( self ):
        tuna.io.read ( "test/unit/unit_io/fake_adhoc.ada" )

    def test_no_file_name ( self ):
        ad = tuna.io.ada ( )
        ad.read ( )

    def test_nonexisting_file ( self ):
        flag = False
        nonexisting_file_number = 0       
        file_name = ""
        
        while not flag:
            nonexisting_file_number += 1            
            file_name = 'adhoc_test_file_' + str ( nonexisting_file_number ) + '.adt'
            try:
                open ( file_name, 'r' )
            except OSError:
                flag = True
        
        # Unless a race condition, adhoc_test_file_?.ad2 does not exist.
        self.assertRaises ( OSError, tuna.io.read, file_name )

    def test_valid_adt_file ( self ):
        tuna.io.read ( "test/unit/unit_io/G093/G093.ADT" )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
