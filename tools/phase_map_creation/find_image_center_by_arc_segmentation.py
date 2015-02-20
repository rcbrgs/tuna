"""
This tool tries to find the center of an image by finding the intersection of rays computed from arc segments.

If a cube is received, it will use the first plane as its input.
"""

from ..get_pixel_neighbours import get_pixel_neighbours
from math import acos, sqrt
import numpy
import random
import sympy
from time import time

class image_center_by_arc_segmentation ( object ):
    def __init__ ( self, ffa_unwrapped = numpy.ndarray ):
        super ( image_center_by_arc_segmentation, self ).__init__ ( )
        self.__i_center_row = None
        self.__i_center_col = None
        self.__ffa_unwrapped = ffa_unwrapped
        random.seed ( )

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
        Tries to find the center by segmenting arcs and searching for the intersection of rays perpendicular to these segments.
        """
        self.detect_ring_borders ( )
        iitl_random_points = [ ]
        for i_points in range ( 4 ):
            i_random_row = random ( 0, self.__ffa_unwrapped.shape [ 0 ] )
            i_random_col = random ( 0, self.__ffa_unwrapped.shape [ 1 ] )
            while ( ( self.__iia_ring_borders [ i_random_row ] [ i_random_col ] == 0 ) or
                    ( ( i_random_row, i_random_col ) in iitl_random_points ) ):
                i_random_row = random ( 0, self.__ffa_unwrapped.shape [ 0 ] )
                i_random_col = random ( 0, self.__ffa_unwrapped.shape [ 1 ] )
            iitl_random_points . append ( ( i_random_row, i_random_col ) )
        print ( iitl_random_points )
        print ( i_median_row, i_median_col )
        o_point_0 = sympy.Point ( iitl_random_points [ 0 ] [ 0 ], iitl_random_points [ 0 ] [ 1 ] )
        o_point_1 = sympy.Point ( iitl_random_points [ 1 ] [ 0 ], iitl_random_points [ 1 ] [ 1 ] )
        o_point_2 = sympy.Point ( iitl_random_points [ 2 ] [ 0 ], iitl_random_points [ 2 ] [ 1 ] )
        o_point_3 = sympy.Point ( iitl_random_points [ 3 ] [ 0 ], iitl_random_points [ 3 ] [ 1 ] )
        o_chord_0 = sympy.geometry.Line ( o_point_0, o_point_1 )
        o_chord_1 = sympy.geometry.Line ( o_point_2, o_point_3 )
        print ( o_chord_0.equation ( ) )
        print ( o_chord_1.equation ( ) )
        o_point_center = sympy.geometry.intersection ( o_chord_0, o_chord_1 )
        print ( o_point_center )
        self.__i_center_row = o_point_center . x
        self.__i_center_col = o_point_center . y
        print ( "Center near ( %d, %d )." % ( self.__i_center_row, self.__i_center_col ) )

    def detect_ring_borders ( self ):
        # detect borders, and select only the first connected set of pixels in this border.
        ring_borders_map = numpy.zeros ( shape = self.__ffa_unwrapped.shape, dtype = numpy.int8 )
        max_x = self.__ffa_unwrapped.shape[0]
        max_y = self.__ffa_unwrapped.shape[1]
        max_channel = numpy.amax ( self.__ffa_unwrapped )
        threshold = max_channel / 2
        for x in range ( max_x ):
            for y in range ( max_y ):
                neighbours = get_pixel_neighbours ( ( x, y ), ring_borders_map )
                for neighbour in neighbours:
                    distance = self.__ffa_unwrapped[x][y] - self.__ffa_unwrapped[neighbour[0]][neighbour[1]]
                    if distance > threshold:
                        ring_borders_map[x][y] = 1
                        break
        # At this point, border pixels have 1, others 0.
        b_first_border_pixel_found = False
        for i_row in range ( max_x ):
            for i_col in range ( max_y ):
                if ( ring_borders [ i_row ] [ i_col ] == 1 ):
                    if b_first_border_pixel_found == False:
                        b_first_border_pixel_found = True
                        ring_borders_map [ i_row ] [ i_col ] = 2
                        continue
                    else:
                        neighbours = get_pixel_neighbours ( ( i_row, i_col ), ring_borders_map )
                        for neighbour in neighbours:
                            if ring_borders_map [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 2:
                                ring_borders_map [ i_row ] [ i_col ] = 2
                                break

        self.__iia_ring_borders = ring_borders_map

        
def find_image_center_by_arc_segmentation ( ffa_unwrapped = numpy.ndarray ):
    """
    Try to find the center of the rings.
    """
    i_start = time ( )
    print ( "find_image_center_by_arc_segmentation", end='' )

    o_finder = image_center_by_arc_segmentation ( ffa_unwrapped = ffa_unwrapped )
    iit_center = o_finder.get_center ( )

    print ( " %ds." % ( time ( ) - i_start ) )
    return iit_center
