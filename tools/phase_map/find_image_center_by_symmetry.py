"""
This tool tries to find the center of an image by finding the row and the column that split the image with the highest degree of symmetry.

If a cube is received, it will use the first plane as its input.
"""

import numpy
from time import time

class image_center_by_symmetry ( object ):
    def __init__ ( self, 
                   array = numpy.ndarray,
                   log = print ):
        super ( image_center_by_symmetry, self ).__init__ ( )
        self.__input_array = None
        self.log = log
        if array.ndim == 2:
            self.__input_array = array
        elif array.ndim == 3:
            self.__input_array = array[0,:,:]
        else:
            self.log ( "Incorrect ndims for input array." )
        self.__center_row = None
        self.__center_col = None

    def get_center ( self ):
        """
        Returns the center coordinates. Will trigger a find if the center is yet unknown.
        """
        if ( ( self.__center_row is not None ) and
             ( self.__center_col is not None ) ):
            return ( self.__center_row, self.__center_col )
        else:
            self.find_center ( )
            return ( self.__center_row, self.__center_col )

    def find_center ( self ):
        """
        Tries to find the center of the image, by splitting the image into same-sized chunks, where the relative distances to the center are the same. The center will have circular symmetry, and therefore these chunks will be very similar.
        """

        input = self.__input_array
        
        #print ( "Searching for most symmetric by-row split." )
        row_results = numpy.ndarray ( shape = ( input.shape[0] ) )
        row_results.fill ( numpy.inf )
        sixteenth = int ( input.shape [ 0 ] / 16 )
        for row in range ( sixteenth, sixteenth * 15 ):
            bottom = input [ row - sixteenth : row - 1, : ]
            top    = input [ row + 1 : row + sixteenth, : ]
            top    = top   [ : : -1, : ]
            difference = bottom - top
            row_results [ row ] = numpy.sum ( numpy.abs ( difference ) )
        #print ( row_results )
        self.__center_row = numpy.argmin ( row_results )

        #print ( "Searching for most symmetric columnar split." )
        col_results = numpy.ndarray ( shape = ( input.shape[1] ) )
        col_results.fill ( numpy.inf )
        sixteenth = int ( input.shape [ 1 ] / 16 )
        for col in range ( sixteenth, sixteenth * 15 ):
            left   = input [ : , col - sixteenth : col - 1 ]
            right  = input [ : , col + 1 : col + sixteenth ]
            right  = right [ : , : : -1 ]
            difference = left - right
            col_results [ col ] = numpy.sum ( numpy.abs ( difference ) )
        #print ( col_results )
        self.__center_col = numpy.argmin ( col_results )

        #print ( "Center near ( %d, %d )." % ( self.__center_row, self.__center_col ) )
        
def find_image_center_by_symmetry ( data = numpy.ndarray,
                                    log = print ):
    """
    Try to find the center of the rings.
    """
    start = time ( )

    o_finder = image_center_by_symmetry ( array = data,
                                          log = log )
    iit_center = o_finder.get_center ( )

    log ( "info: find_image_center_by_symmetry() took %ds." % ( time ( ) - start ) )
    return iit_center
