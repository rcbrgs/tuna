"""
This tool tries to find the center of an image by finding the intersection of rays computed from arc segments.

If a cube is received, it will use the first plane as its input.
"""

#from ..get_pixel_neighbours import get_pixel_neighbours
from math import acos, sqrt
import numpy
import random
import sympy
from time import time
import tuna

class image_center_by_arc_segmentation ( object ):
    def __init__ ( self, 
                   wrapped,
                   log = print ):
        super ( image_center_by_arc_segmentation, self ).__init__ ( )
        self.__center_row = None
        self.__center_col = None
        self.log = log
        self.wrapped = wrapped
        random.seed ( )

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
        Tries to find the center by segmenting arcs and searching for the intersection of rays perpendicular to these segments.
        """
        self.detect_ring_borders ( )

        convergence_tries = 1
        bisections = [ ]
        centers = [ ]
        while ( True ):
            chord_bisector_0 = self.get_random_chord_bisector ( )
            chord_bisector_1 = self.get_random_chord_bisector ( )
            while ( sympy.Line.is_parallel ( chord_bisector_0, chord_bisector_1 ) ):
                chord_bisector_0 = self.get_random_chord_bisector ( )
                chord_bisector_1 = self.get_random_chord_bisector ( )
                    
            #self.log ( "o_chord_bisector_0 = %s, slope = %s" % ( str ( chord_bisector_0.equation ( ) ), str ( float ( chord_bisector_0.slope.evalf ( ) ) ) ) )
            #self.log ( "o_chord_bisector_1 = %s, slope = %s" % ( str ( chord_bisector_1.equation ( ) ), str ( float ( chord_bisector_1.slope.evalf ( ) ) ) ) )
            bisections.append ( ( chord_bisector_0, chord_bisector_1, convergence_tries * 10 ) )

            # sometimes intesection fails because one of the bisectors ain't a GeometryEntity.
            try:
                intersection = sympy.geometry.intersection ( chord_bisector_0, chord_bisector_1 )
            except ValueError as e:
                self.log ( "warning: ValueError %s. Ignoring this intersection." % ( e ) )
                convergence_tries += 1
                continue

            if ( len ( intersection ) != 0 ):
                point_center = intersection [ 0 ]
                intersect_row = int ( point_center.x.evalf ( ) )
                intersect_col = int ( point_center.y.evalf ( ) )
                #self.log ( "o_point_center = %s" % str ( ( intersect_row, intersect_col ) ) )
                #self.log ( "i_convergence_tries * 10 = %s" % str ( convergence_tries * 10 ) )
                centers.append ( ( int ( intersect_row ), int ( intersect_col ) ) )
                sum_row = 0
                sum_col = 0
                for center in range ( len ( centers ) ):
                    sum_row +=  centers [ center ] [ 0 ]
                    sum_col +=  centers [ center ] [ 1 ]
                center = ( int ( sum_row / len ( centers ) ),
                             int ( sum_col / len ( centers ) ) )
                #self.log ( "t_center now at %s" % str ( center ) )
            convergence_tries += 1
            if ( convergence_tries > 10 ):
                if ( center == ( intersect_row, intersect_col ) ):
                    #self.log ( "t_center converged at %s" % str ( center ) )
                    break
                if ( convergence_tries > 1000 ):
                    self.log ( "warning: Reached threshold for center convergence using chord perpendiculars." )
                    break
        # plot bisection lines for debug: (very slow)
        #for bisection in range ( len ( bisections ) ):
        #    self.plot_line ( line = bisections [ bisection ] [ 0 ], color = bisections [ bisection ] [ 2 ] )
        #    self.plot_line ( line = bisections [ bisection ] [ 1 ], color = bisections [ bisection ] [ 2 ] )

        self.__center_row = center [ 0 ]
        self.__center_col = center [ 1 ]

    def detect_ring_borders ( self ):
        """
        Detect borders, and select only the first connected set of pixels in this border.
        """
        ring_borders_map = numpy.zeros ( shape = self.wrapped.shape, dtype = numpy.int16 )
        max_rows = self.wrapped.shape[0]
        max_cols = self.wrapped.shape[1]
        max_channel = numpy.amax ( self.wrapped.array )
        channel_threshold = max_channel - 1

        for row in range ( max_rows ):
            for col in range ( max_cols ):
                neighbours = tuna.tools.get_pixel_neighbours ( ( row, col ), ring_borders_map )
                distances = [ ]
                for neighbour in neighbours:
                    distances.append ( int ( abs ( self.wrapped.array [ row ] [ col ] - 
                                                   self.wrapped.array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] ) ) )
                max_distance = max ( distances )
                if ( max_distance > channel_threshold and
                     int ( self.wrapped.array [ row ] [ col ] ) == 0 ):
                    ring_borders_map [ row ] [ col ] = 1
        if ( numpy.sum ( ring_borders_map ) == 0 ):
            self.log ( "warning: No borders detected." )
            self.__ring_borders = numpy.ones ( shape = ring_borders_map.shape )
            return

        # color continuous ring borders with different colors
        next_color = 2
        for row in range ( max_rows ):
            #self.log ( "i_row = %d" % row )
            for col in range ( max_cols ):
                if ring_borders_map [ row ] [ col ] == 1:
                    borderhood = [ ( row, col ) ]
                    while ( borderhood != [ ] ):
                        #self.log ( "l_borderhood = %s" % str ( borderhood ) )
                        tocolor_pixel = borderhood.pop ( )
                        neighbours = tuna.tools.get_pixel_neighbours ( ( tocolor_pixel [ 0 ], tocolor_pixel [ 1 ] ), ring_borders_map )
                        for neighbour in neighbours:
                            if neighbour not in borderhood:
                                if ring_borders_map [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                                    borderhood.append ( neighbour )
                        ring_borders_map [ tocolor_pixel [ 0 ] ] [ tocolor_pixel [ 1 ] ] = next_color
                    next_color += 1
                
        # how many pixels are colored in each color?
        color_counts = { }
        for row in range ( max_rows ):
            for col in range ( max_cols ):
                color = ring_borders_map [ row ] [ col ]
                if color > 0:
                    if color in color_counts.keys ( ):
                        color_counts [ color ] += 1
                    else:
                        color_counts [ color ] = 1

        # filter out everything but the largest arc
        if ( color_counts == { } ):
            self.log ( "debug: color_counts == { }" )
        else:
            max_arc_count = max ( color_counts.values ( ) )
            for color, count in color_counts.items ( ):
                if count == max_arc_count:
                    max_arc_color = color
                    break
            #self.log ( "i_max_arc_color, max_arc_count = %d, %d" % ( max_arc_color, max_arc_count ) )
            for row in range ( max_rows ):
                for col in range ( max_cols ):
                    if ring_borders_map [ row ] [ col ] != max_arc_color:
                        ring_borders_map [ row ] [ col ] = 0
                    else:
                        ring_borders_map [ row ] [ col ] = 1

        self.__ring_borders = numpy.copy ( ring_borders_map )

    def get_most_distant_points ( self, tl_points = [ ] ):
        max_distance = 0
        max_origin = 0
        max_destiny = 0
        for origin in range ( len ( tl_points ) ):
            for destiny in range ( origin + 1, len ( tl_points ) ):
                distance = sqrt ( ( tl_points [ origin ] [ 0 ] - tl_points [ destiny ] [ 0 ] ) ** 2 +
                                    ( tl_points [ origin ] [ 1 ] - tl_points [ destiny ] [ 1 ] ) ** 2 )
                if ( distance >= max_distance ):
                    max_distance = distance
                    max_origin = origin
                    max_destiny = destiny
        return [ tl_points [ max_origin ], tl_points [ max_destiny ] ]

    def get_random_chord_bisector ( self ):
        random_points = [ ]
        for points in range ( 3 ):
            random_points . append ( self.get_random_point_in_border ( ) )
        max_distance_points = self.get_most_distant_points ( random_points )
        point_0 = sympy.Point ( max_distance_points [ 0 ] [ 0 ], max_distance_points [ 0 ] [ 1 ] )
        point_1 = sympy.Point ( max_distance_points [ 1 ] [ 0 ], max_distance_points [ 1 ] [ 1 ] )
        #self.log ( "debug: point_0, point_1 = %s, %s" % ( str ( point_0 ), str ( point_1 ) ) )
        chord_segment = sympy.Segment ( point_0, point_1 )
        if ( type ( chord_segment ) is sympy.Point ):
            self.log ( "error: Segmentation created a point." )
            return None
        return chord_segment.perpendicular_bisector ( )

    def get_random_point_in_border ( self ):
        random_row = random.randint ( 0, self.wrapped.shape [ 0 ] - 1 )
        random_col = random.randint ( 0, self.wrapped.shape [ 1 ] - 1 )
        random_color = self.__ring_borders [ random_row ] [ random_col ]
        while ( random_color == 0 ):
            random_row = random.randint ( 0, self.wrapped.shape [ 0 ] - 1 )
            random_col = random.randint ( 0, self.wrapped.shape [ 1 ] - 1 )
            random_color = self.__ring_borders [ random_row ] [ random_col ]
        return ( random_row, random_col )

    def plot_line ( self, line, color ):
        max_rows = self.__ring_borders.shape [ 0 ]
        max_cols = self.__ring_borders.shape [ 1 ]
        coeff_x = line.coefficients [ 0 ].evalf ( )
        coeff_y = line.coefficients [ 1 ].evalf ( )
        coeff_C = line.coefficients [ 2 ].evalf ( )
        coefficients = [ coeff_x, coeff_y, coeff_C ]
        for row in range ( max_rows ):
            for col in range ( max_cols ):
                result = ( ( coefficients [ 0 ] * row ) + 
                             ( coefficients [ 1 ] * col ) + 
                             ( coefficients [ 2 ] ) )
                if ( abs ( result ) < 100 ):
                    self.__ring_borders [ row ] [ col ] = color

def find_image_center_by_arc_segmentation ( wrapped,
                                            log = print ):
    """
    Try to find the center of the rings.
    """
    start = time ( )

    log ( "info: trying to find_image_center_by_arc_segmentation()." )

    if not isinstance ( wrapped, tuna.io.can ):
        log ( "error: unexpected value for parameter." )
        return None

    finder = image_center_by_arc_segmentation ( wrapped = wrapped,
                                                log = log )
    center = finder.get_center ( )
    log ( "info: Center detected at %s ." % str ( center ) )

    log ( "info: find_image_center_by_arc_segmentation() took %ds." % ( time ( ) - start ) )
    return center
