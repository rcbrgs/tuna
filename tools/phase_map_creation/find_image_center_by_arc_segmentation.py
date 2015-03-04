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
    def __init__ ( self, log = print, ffa_unwrapped = numpy.ndarray ):
        super ( image_center_by_arc_segmentation, self ).__init__ ( )
        self.__i_center_row = None
        self.__i_center_col = None
        self.log = log
        self.__ffa_unwrapped = ffa_unwrapped
        random.seed ( )

    def get_center ( self ):
        """
        Returns the center coordinates. Will trigger a find if the center is yet unknown.
        """
        if ( ( self.__i_center_row is not None ) and
             ( self.__i_center_col is not None ) ):
            return ( self.__i_center_row, self.__i_center_col ), self.__iia_ring_borders
        else:
            self.find_center ( )
            return ( self.__i_center_row, self.__i_center_col ), self.__iia_ring_borders

    def find_center ( self ):
        """
        Tries to find the center by segmenting arcs and searching for the intersection of rays perpendicular to these segments.
        """
        self.detect_ring_borders ( )
        t_center = ( 0, 0 )
        i_intersect_row = -1
        i_intersect_col = -1
        i_convergence_tries = 1

        while ( t_center != ( i_intersect_row, i_intersect_col ) ):
            o_chord_bisector_0 = self.get_random_chord_bisector ( )
            o_chord_bisector_1 = self.get_random_chord_bisector ( )
            self.log ( "o_chord_bisector_0 = %s, slope = %s" % ( str ( o_chord_bisector_0.equation ( ) ), str ( float ( o_chord_bisector_0.slope.evalf ( ) ) ) ) )
            self.log ( "o_chord_bisector_1 = %s, slope = %s" % ( str ( o_chord_bisector_1.equation ( ) ), str ( float ( o_chord_bisector_1.slope.evalf ( ) ) ) ) )
            l_lines_to_plot = [ o_chord_bisector_0, o_chord_bisector_1 ]
            self.plot_lines ( l_lines = l_lines_to_plot, i_color = i_convergence_tries * 10 )
            ol_intersection = sympy.geometry.intersection ( o_chord_bisector_0, o_chord_bisector_1 )
            if ( len ( ol_intersection ) != 0 ):
                o_point_center = ol_intersection [ 0 ]
                i_intersect_row = int ( o_point_center.x.evalf ( ) )
                i_intersect_col = int ( o_point_center.y.evalf ( ) )
                self.log ( "o_point_center = %s" % str ( ( i_intersect_row, i_intersect_col ) ) )
                self.log ( "i_convergence_tries * 10 = %s" % str ( i_convergence_tries * 10 ) )
                t_center = ( int ( ( t_center [ 0 ] + 2 * i_intersect_row ) / 3 ),
                             int ( ( t_center [ 1 ] + 2 * i_intersect_col ) / 3 ) )
                self.log ( "t_center now at %s" % str ( t_center ) )
            i_convergence_tries += 1
            if ( i_convergence_tries > 10 ):
                self.log ( "Threshold for convergence reached." )
                break

        self.__i_center_row = t_center [ 0 ]
        self.__i_center_col = t_center [ 1 ]
        print ( "Center near ( %d, %d )." % ( self.__i_center_row, self.__i_center_col ) )

    def detect_ring_borders ( self ):
        """
        Detect borders, and select only the first connected set of pixels in this border.
        """
        ring_borders_map = numpy.zeros ( shape = self.__ffa_unwrapped.shape, dtype = numpy.int16 )
        max_rows = self.__ffa_unwrapped.shape[0]
        max_cols = self.__ffa_unwrapped.shape[1]
        max_channel = numpy.amax ( self.__ffa_unwrapped )
        threshold = max_channel - 1
        i_next_color = 10
        d_color_counts = { }
        for i_row in range ( max_rows ):
            for i_col in range ( max_cols ):
                neighbours = get_pixel_neighbours ( ( i_row, i_col ), ring_borders_map )
                il_distances = [ ]
                il_colors = [ ]
                for neighbour in neighbours:
                    il_distances.append ( int ( abs ( self.__ffa_unwrapped [ i_row ] [ i_col ] - 
                                                      self.__ffa_unwrapped [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] ) ) )
                    il_colors.append ( ring_borders_map [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] )
                i_max_distance = max ( il_distances )
                if ( i_max_distance > threshold and
                     int ( self.__ffa_unwrapped [ i_row ] [ i_col ] ) == 0 ):
                    i_color = max ( il_colors )
                    if ( i_color == 0 ):
                        i_color = i_next_color
                        i_next_color += 1

                    ring_borders_map [ i_row ] [ i_col ] = int ( i_color )
                    if i_color in d_color_counts.keys ( ):
                        d_color_counts [ i_color ] += 1
                    else:
                        d_color_counts [ i_color ] = 1

                    #neighbours = get_pixel_neighbours ( ( i_row, i_col ), ring_borders_map )
                    #for neighbour in neighbours:
                    #    if int ( self.__ffa_unwrapped [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] ) == 0:
                    #        ring_borders_map [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] = int ( i_color )
                    #        if i_color in d_color_counts.keys ( ):
                    #            d_color_counts [ i_color ] += 1
                    #        else:
                    #            d_color_counts [ i_color ] = 1

        # filter out everything but the largest arc
        i_max_arc_count = max ( d_color_counts.values ( ) )
        for i_color, i_count in d_color_counts.items ( ):
            if i_count == i_max_arc_count:
                i_max_arc_color = i_color
                break
        self.log ( "i_max_arc_color, i_max_arc_count = %d, %d" % ( i_max_arc_color, i_max_arc_count ) )
        for i_row in range ( max_rows ):
            for i_col in range ( max_cols ):
                if ring_borders_map [ i_row ] [ i_col ] != i_max_arc_color:
                    ring_borders_map [ i_row ] [ i_col ] = 0
                else:
                    ring_borders_map [ i_row ] [ i_col ] = 1

        self.__iia_ring_borders = numpy.copy ( ring_borders_map )

    def get_most_distant_points ( self, tl_points = [ ] ):
        f_max_distance = 0
        i_max_origin = 0
        i_max_destiny = 0
        for i_origin in range ( len ( tl_points ) ):
            for i_destiny in range ( i_origin + 1, len ( tl_points ) ):
                f_distance = sqrt ( ( tl_points [ i_origin ] [ 0 ] - tl_points [ i_destiny ] [ 0 ] ) ** 2 +
                                    ( tl_points [ i_origin ] [ 1 ] - tl_points [ i_destiny ] [ 1 ] ) ** 2 )
                if ( f_distance >= f_max_distance ):
                    f_max_distance = f_distance
                    i_max_origin = i_origin
                    i_max_destiny = i_destiny
        return [ tl_points [ i_max_origin ], tl_points [ i_max_destiny ] ]

    def get_random_chord_bisector ( self ):
        l_random_points = [ ]
        for i_points in range ( 3 ):
            l_random_points . append ( self.get_random_point_in_border ( ) )
        l_max_distance_points = self.get_most_distant_points ( l_random_points )
        o_point_0 = sympy.Point ( l_max_distance_points [ 0 ] [ 0 ], l_max_distance_points [ 0 ] [ 1 ] )
        o_point_1 = sympy.Point ( l_max_distance_points [ 1 ] [ 0 ], l_max_distance_points [ 1 ] [ 1 ] )
        self.log ( "o_point_0, o_point_1 = %s, %s" % ( str ( o_point_0 ), str ( o_point_1 ) ) )
        o_chord_segment = sympy.Segment ( o_point_0, o_point_1 )
        return o_chord_segment.perpendicular_bisector ( )

    def get_random_point_in_border ( self ):
        i_random_row = random.randint ( 0, self.__ffa_unwrapped.shape [ 0 ] - 1 )
        i_random_col = random.randint ( 0, self.__ffa_unwrapped.shape [ 1 ] - 1 )
        i_random_color = self.__iia_ring_borders [ i_random_row ] [ i_random_col ]
        while ( i_random_color == 0 ):
            i_random_row = random.randint ( 0, self.__ffa_unwrapped.shape [ 0 ] - 1 )
            i_random_col = random.randint ( 0, self.__ffa_unwrapped.shape [ 1 ] - 1 )
            i_random_color = self.__iia_ring_borders [ i_random_row ] [ i_random_col ]
        return ( i_random_row, i_random_col )

    def plot_lines ( self, l_lines, i_color ):
        max_rows = self.__ffa_unwrapped.shape [ 0 ]
        max_cols = self.__ffa_unwrapped.shape [ 1 ]
        d_coefficients = { }
        for i_line in range ( len ( l_lines ) ):
            f_coeff_x = l_lines [ i_line ].coefficients [ 0 ].evalf ( )
            f_coeff_y = l_lines [ i_line ].coefficients [ 1 ].evalf ( )
            f_coeff_C = l_lines [ i_line ].coefficients [ 2 ].evalf ( )
            d_coefficients [ i_line ] = ( f_coeff_x, f_coeff_y, f_coeff_C )
        for i_row in range ( max_rows ):
            for i_col in range ( max_cols ):
                for i_line in range ( len ( l_lines ) ): 
                    f_result = ( ( d_coefficients [ i_line ] [ 0 ] * i_row ) + 
                                 ( d_coefficients [ i_line ] [ 1 ] * i_col ) + 
                                 ( d_coefficients [ i_line ] [ 2 ] ) )
                    if ( abs ( f_result ) < 3 ):
                        self.__iia_ring_borders [ i_row ] [ i_col ] = i_color
                        break
        
def find_image_center_by_arc_segmentation ( ffa_unwrapped = numpy.ndarray ):
    """
    Try to find the center of the rings.
    """
    i_start = time ( )
    print ( "find_image_center_by_arc_segmentation", end='' )

    o_finder = image_center_by_arc_segmentation ( ffa_unwrapped = ffa_unwrapped )
    iit_center, borders = o_finder.get_center ( )

    print ( " %ds." % ( time ( ) - i_start ) )
    return iit_center, borders.astype ( numpy.float64 )
