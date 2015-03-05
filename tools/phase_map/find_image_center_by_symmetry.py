"""
This tool tries to find the center of an image by finding the row and the column that split the image with the highest degree of symmetry.

If a cube is received, it will use the first plane as its input.
"""

import numpy
from time import time

class image_center_by_symmetry ( object ):
    def __init__ ( self, ia_array = numpy.ndarray ):
        super ( image_center_by_symmetry, self ).__init__ ( )
        self.__ia_input_array = None
        if ia_array.ndim == 2:
            self.__ia_input_array = ia_array
        elif ia_array.ndim == 3:
            self.__ia_input_array = ia_array[0,:,:]
        else:
            print ( "Incorrect ndims for input array." )
        self.__i_center_row = None
        self.__i_center_col = None
        

    def get_center ( self ):
        """
        Returns the center coordinates. Will trigger a find if the center is yet unknown.
        """
        if ( ( self.__i_center_row is not None ) and
             ( self.__i_center_col is not None ) ):
            return ( self.__i_center_row, self.__i_center_col )
        else:
            self.find_center ( )
            return ( self.__i_center_row, self.__i_center_col )

    def find_center ( self ):
        """
        Tries to find the center of the image, by splitting the image into same-sized chunks, where the relative distances to the center are the same. The center will have circular symmetry, and therefore these chunks will be very similar.
        """

        ia_input = self.__ia_input_array
        
        #print ( "Searching for most symmetric by-row split." )
        ia_row_results = numpy.ndarray ( shape = ( ia_input.shape[0] ) )
        ia_row_results.fill ( numpy.inf )
        i_sixteenth = int ( ia_input.shape [ 0 ] / 16 )
        for i_row in range ( i_sixteenth, i_sixteenth * 15 ):
            ia_bottom = ia_input [ i_row - i_sixteenth : i_row - 1, : ]
            ia_top    = ia_input [ i_row + 1 : i_row + i_sixteenth, : ]
            ia_top    = ia_top   [ : : -1, : ]
            ia_difference = ia_bottom - ia_top
            ia_row_results [ i_row ] = numpy.sum ( numpy.abs ( ia_difference ) )
        #print ( ia_row_results )
        self.__i_center_row = numpy.argmin ( ia_row_results )

        #print ( "Searching for most symmetric columnar split." )
        ia_col_results = numpy.ndarray ( shape = ( ia_input.shape[1] ) )
        ia_col_results.fill ( numpy.inf )
        i_sixteenth = int ( ia_input.shape [ 1 ] / 16 )
        for i_col in range ( i_sixteenth, i_sixteenth * 15 ):
            ia_left   = ia_input [ : , i_col - i_sixteenth : i_col - 1 ]
            ia_right  = ia_input [ : , i_col + 1 : i_col + i_sixteenth ]
            ia_right  = ia_right [ : , : : -1 ]
            ia_difference = ia_left - ia_right
            ia_col_results [ i_col ] = numpy.sum ( numpy.abs ( ia_difference ) )
        #print ( ia_col_results )
        self.__i_center_col = numpy.argmin ( ia_col_results )

        #print ( "Center near ( %d, %d )." % ( self.__i_center_row, self.__i_center_col ) )
        
def find_image_center_by_symmetry ( ia_data = numpy.ndarray ):
    """
    Try to find the center of the rings.
    """
    i_start = time ( )
    print ( "find_image_center_by_symmetry", end='' )

    o_finder = image_center_by_symmetry ( ia_array = ia_data )
    iit_center = o_finder.get_center ( )

    print ( " %ds." % ( time ( ) - i_start ) )
    return iit_center
