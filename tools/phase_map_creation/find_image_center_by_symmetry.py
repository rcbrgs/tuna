"""
This tool tries to find the center of an image by finding the row and the column that split the image with the highest degree of symmetry.

If a cube is received, it will use the first plane as its input.
"""

import numpy

class find_image_center_by_symmetry ( object ):
    def __init__ ( self, ia_array = numpy.ndarray ):
        super ( find_image_center_by_symmetry, self ).__init__ ( )
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
        Tries to find the center of the image, by splitting the image into halves and subtracting same-sized chunks of the halves, where the relative distances to the center are the same.
        """

        ia_input = self.__ia_input_array
        
        print ( "Searching for most symmetric by-row split." )
        ia_row_results = numpy.zeros ( shape = ( ia_input.shape[0] ) )
        for i_current_guess_row in range ( int ( ia_input.shape[0] / 16 ), int ( ia_input.shape[0] / 16 ) * 15 ):
            ia_bottom = ia_input[:i_current_guess_row - 1,:]
            ia_top    = ia_input[i_current_guess_row + 1:,:]
            i_row_guess_max = min ( [ia_bottom.shape[0], ia_top.shape[0]] ) - 1
            ia_bottom = ia_bottom[:i_row_guess_max,:]
            ia_top    = ia_top   [:i_row_guess_max,:]
            ia_top    = ia_top   [::-1,:]
            ia_row_guess_differences = ia_bottom - ia_top
            ia_row_results[i_current_guess_row] = - numpy.sum ( numpy.abs ( ia_row_guess_differences ) )
        self.__i_center_row = numpy.argmin ( ia_row_results )

        print ( "Searching for most symmetric columnar split." )
        ia_col_results = numpy.zeros ( shape = ( ia_input.shape[1] ) )
        for i_current_guess_col in range ( int ( ia_input.shape[1] / 16 ), int ( ia_input.shape[1] / 16 ) * 15 ):
            ia_left   = ia_input[:,:i_current_guess_col - 1]
            ia_right  = ia_input[:,i_current_guess_col + 1:]
            i_col_guess_max = min ( [ia_left.shape[1], ia_right.shape[1]] ) - 1
            ia_left   = ia_left  [:,:i_col_guess_max]
            ia_right  = ia_right [:,:i_col_guess_max]
            ia_right  = ia_right [:,::-1]
            ia_col_guess_differences = ia_left - ia_right
            ia_col_results[i_current_guess_col] = - numpy.sum ( numpy.abs ( ia_col_guess_differences ) )
        self.__i_center_col = numpy.argmin ( ia_col_results )
