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
            return ( self.__i_center_row, self.__i_center_col )
        else:
            self.find_center ( )
            return ( self.__i_center_row, self.__i_center_col )

    def find_center ( self ):
        """
        Tries to find the center by segmenting arcs and searching for the intersection of rays perpendicular to these segments.
        """
        self.detect_ring_borders ( )

        i_convergence_tries = 1
        l_bisections = [ ]
        l_centers = [ ]
        while ( True ):
            o_chord_bisector_0 = self.get_random_chord_bisector ( )
            o_chord_bisector_1 = self.get_random_chord_bisector ( )
            while ( sympy.Line.is_parallel ( o_chord_bisector_0, o_chord_bisector_1 ) ):
                    o_chord_bisector_0 = self.get_random_chord_bisector ( )
                    o_chord_bisector_1 = self.get_random_chord_bisector ( )
                    
            #self.log ( "o_chord_bisector_0 = %s, slope = %s" % ( str ( o_chord_bisector_0.equation ( ) ), str ( float ( o_chord_bisector_0.slope.evalf ( ) ) ) ) )
            #self.log ( "o_chord_bisector_1 = %s, slope = %s" % ( str ( o_chord_bisector_1.equation ( ) ), str ( float ( o_chord_bisector_1.slope.evalf ( ) ) ) ) )
            l_bisections.append ( ( o_chord_bisector_0, o_chord_bisector_1, i_convergence_tries * 10 ) )
            ol_intersection = sympy.geometry.intersection ( o_chord_bisector_0, o_chord_bisector_1 )
            if ( len ( ol_intersection ) != 0 ):
                o_point_center = ol_intersection [ 0 ]
                i_intersect_row = int ( o_point_center.x.evalf ( ) )
                i_intersect_col = int ( o_point_center.y.evalf ( ) )
                #self.log ( "o_point_center = %s" % str ( ( i_intersect_row, i_intersect_col ) ) )
                #self.log ( "i_convergence_tries * 10 = %s" % str ( i_convergence_tries * 10 ) )
                l_centers.append ( ( int ( i_intersect_row ), int ( i_intersect_col ) ) )
                i_sum_row = 0
                i_sum_col = 0
                for i_center in range ( len ( l_centers ) ):
                    i_sum_row +=  l_centers [ i_center ] [ 0 ]
                    i_sum_col +=  l_centers [ i_center ] [ 1 ]
                t_center = ( int ( i_sum_row / len ( l_centers ) ),
                             int ( i_sum_col / len ( l_centers ) ) )
                #self.log ( "t_center now at %s" % str ( t_center ) )
            i_convergence_tries += 1
            if ( i_convergence_tries > 10 ):
                if ( t_center == ( i_intersect_row, i_intersect_col ) ):
                    #self.log ( "t_center converged at %s" % str ( t_center ) )
                    break
                if ( i_convergence_tries > 1000 ):
                    self.log ( "warning: Reached threshold for center convergence using chord perpendiculars." )
                    break
        # plot bisection lines for debug: (very slow)
        #for i_bisection in range ( len ( l_bisections ) ):
        #    self.plot_line ( o_line = l_bisections [ i_bisection ] [ 0 ], i_color = l_bisections [ i_bisection ] [ 2 ] )
        #    self.plot_line ( o_line = l_bisections [ i_bisection ] [ 1 ], i_color = l_bisections [ i_bisection ] [ 2 ] )

        self.__i_center_row = t_center [ 0 ]
        self.__i_center_col = t_center [ 1 ]
        #print ( "Center near ( %d, %d )." % ( self.__i_center_row, self.__i_center_col ) )

    def detect_ring_borders ( self ):
        """
        Detect borders, and select only the first connected set of pixels in this border.
        """
        ring_borders_map = numpy.zeros ( shape = self.__ffa_unwrapped.shape, dtype = numpy.int16 )
        max_rows = self.__ffa_unwrapped.shape[0]
        max_cols = self.__ffa_unwrapped.shape[1]
        max_channel = numpy.amax ( self.__ffa_unwrapped )
        f_channel_threshold = max_channel - 1

        for i_row in range ( max_rows ):
            for i_col in range ( max_cols ):
                neighbours = get_pixel_neighbours ( ( i_row, i_col ), ring_borders_map )
                l_distances = [ ]
                for neighbour in neighbours:
                    l_distances.append ( int ( abs ( self.__ffa_unwrapped [ i_row ] [ i_col ] - 
                                                     self.__ffa_unwrapped [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] ) ) )
                f_max_distance = max ( l_distances )
                if ( f_max_distance > f_channel_threshold and
                     int ( self.__ffa_unwrapped [ i_row ] [ i_col ] ) == 0 ):
                    ring_borders_map [ i_row ] [ i_col ] = 1
        if ( numpy.sum ( ring_borders_map ) == 0 ):
            self.log ( "warning: No borders detected." )
            self.__iia_ring_borders = numpy.ones ( shape = ring_borders_map.shape )
            return

        # color continuous ring borders with different colors
        i_next_color = 2
        for i_row in range ( max_rows ):
            #self.log ( "i_row = %d" % i_row )
            for i_col in range ( max_cols ):
                if ring_borders_map [ i_row ] [ i_col ] == 1:
                    l_borderhood = [ ( i_row, i_col ) ]
                    while ( l_borderhood != [ ] ):
                        #self.log ( "l_borderhood = %s" % str ( l_borderhood ) )
                        t_tocolor_pixel = l_borderhood.pop ( )
                        l_neighbours = get_pixel_neighbours ( ( t_tocolor_pixel [ 0 ], t_tocolor_pixel [ 1 ] ), ring_borders_map )
                        for t_neighbour in l_neighbours:
                            if t_neighbour not in l_borderhood:
                                if ring_borders_map [ t_neighbour [ 0 ] ] [ t_neighbour [ 1 ] ] == 1:
                                    l_borderhood.append ( t_neighbour )
                        ring_borders_map [ t_tocolor_pixel [ 0 ] ] [ t_tocolor_pixel [ 1 ] ] = i_next_color
                    i_next_color += 1
                
        # how many pixels are colored in each color?
        d_color_counts = { }
        for i_row in range ( max_rows ):
            for i_col in range ( max_cols ):
                i_color = ring_borders_map [ i_row ] [ i_col ]
                if i_color > 0:
                    if i_color in d_color_counts.keys ( ):
                        d_color_counts [ i_color ] += 1
                    else:
                        d_color_counts [ i_color ] = 1

        # filter out everything but the largest arc
        if ( d_color_counts == { } ):
            self.log ( "debug: d_color_counts == { }" )
        else:
            i_max_arc_count = max ( d_color_counts.values ( ) )
            for i_color, i_count in d_color_counts.items ( ):
                if i_count == i_max_arc_count:
                    i_max_arc_color = i_color
                    break
            #self.log ( "i_max_arc_color, i_max_arc_count = %d, %d" % ( i_max_arc_color, i_max_arc_count ) )
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
        #self.log ( "debug: o_point_0, o_point_1 = %s, %s" % ( str ( o_point_0 ), str ( o_point_1 ) ) )
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

    def plot_line ( self, o_line, i_color ):
        max_rows = self.__iia_ring_borders.shape [ 0 ]
        max_cols = self.__iia_ring_borders.shape [ 1 ]
        f_coeff_x = o_line.coefficients [ 0 ].evalf ( )
        f_coeff_y = o_line.coefficients [ 1 ].evalf ( )
        f_coeff_C = o_line.coefficients [ 2 ].evalf ( )
        d_coefficients = [ f_coeff_x, f_coeff_y, f_coeff_C ]
        for i_row in range ( max_rows ):
            for i_col in range ( max_cols ):
                f_result = ( ( d_coefficients [ 0 ] * i_row ) + 
                             ( d_coefficients [ 1 ] * i_col ) + 
                             ( d_coefficients [ 2 ] ) )
                if ( abs ( f_result ) < 100 ):
                    self.__iia_ring_borders [ i_row ] [ i_col ] = i_color

def find_image_center_by_arc_segmentation ( ffa_unwrapped = numpy.ndarray,
                                            log = print ):
    """
    Try to find the center of the rings.
    """
    i_start = time ( )

    o_finder = image_center_by_arc_segmentation ( ffa_unwrapped = ffa_unwrapped,
                                                  log = log )
    iit_center = o_finder.get_center ( )

    log ( "info: find_image_center_by_arc_segmentation() took %ds." % ( time ( ) - i_start ) )
    return iit_center
