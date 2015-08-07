import logging
import numpy
import os
import tuna
import unittest

class unit_test_io_can ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "nose.log" )

    def test_add ( self ):
        z1 = numpy.zeros ( shape = ( 1, 2, 3 ) )
        z2 = numpy.ones ( shape = ( 1, 2, 3 ) )
        z3 = z1 + z2
        self.assertTrue ( numpy.array_equal ( z3, z2 ) )

    def test_convert_to_table ( self ):
        file_name = "test/unit/unit_io/adhoc.ad2"
        can = tuna.io.read ( file_name )
        table = can.convert_ndarray_into_table ( )

    def test_subtract ( self ):
        z1 = numpy.ones ( shape = ( 1, 2, 3 ) )
        z2 = numpy.ones ( shape = ( 1, 2, 3 ) )
        z3 = z1 - z2
        z4 = numpy.zeros ( shape = ( 1, 2, 3 ) )
        self.assertTrue ( numpy.array_equal ( z3, z4 ) )

    def test_write ( self ):
        file_name = "../test_write.fits"
        if ( os.path.isfile ( file_name ) ):
            os.remove ( file_name )

        array = numpy.zeros ( shape = ( 2, 2, 2 ) )
        tuna.io.write ( file_name = file_name, array = array, file_format = 'fits' )

        if ( os.path.isfile ( file_name ) ):
            os.remove ( file_name )

    def test_write_file_exists ( self ):
        file_name = "../test_write.fits"
        if ( os.path.isfile ( file_name ) ):
            os.remove ( file_name )

        array = numpy.zeros ( shape = ( 2, 2, 2 ) )
        tuna.io.write ( file_name = file_name, array = array, file_format = 'fits' )
        tuna.io.write ( file_name = file_name, array = array, file_format = 'fits' )

        if ( os.path.isfile ( file_name ) ):
            os.remove ( file_name )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
