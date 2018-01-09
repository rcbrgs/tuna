"""
This module's scope are the procedures necessary to find the center in a spectrograph using the arc segmentation method.
"""

import logging
from math import acos, sqrt
import numpy
import random
import sympy
import threading
import time
import tuna

class arc_segmentation_center_finder ( threading.Thread ):
    """
    This class' responsibility is to find the center of an image by finding the intersection of rays computed from arc segments.
    
    If a cube is received, it will use the first plane as its input.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor expects the following parameters:

    * noise : can
        Containing the noise related to the data at hand.

    * wrapped : can
        Containing a wrapped phase map, such as one generated by one of the barycenter's tools in Tuna.

    Example:

        >>> import tuna
        >>> barycenter = tuna.io.read ( "tuna/test/unit/unit_io/G094_03_wrapped_phase_map.fits" )
        >>> noise = tuna.io.read ( "tuna/test/unit/unit_io/G094_04_noise.fits" )
        >>> center = tuna.tools.phase_map.arc_segmentation_center_finder ( noise = noise, wrapped = barycenter ); center.join ( )
        >>> center.get_center ( )
        (218, 254)

    """
    def __init__ ( self, wrapped, noise ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.0"
        self.changelog = {
            "0.1.0" : "Tuna 0.14.0 : improved documentation, silenced logs."
            }

        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.noise = noise
        self.wrapped = wrapped
        
        self.center = None
        self.__center_row = None
        self.__center_col = None

        random.seed ( )
        self.start ( )

    def run ( self ):
        """
        This method's goal is to execute the main algorithm once its  thread .start ( ) method is called.
        """
        start = time.time ( )

        self.log.debug ( "Trying to find_image_center_by_arc_segmentation()." )

        if not isinstance ( self.wrapped, tuna.io.can.Can ):
            self.log.error ( "Unexpected value for parameter." )
            return None

        self.center = self.get_center ( )
        self.log.debug ( "Center detected at %s." % str ( self.center ) )

        self.log.debug ( "find_image_center_by_arc_segmentation() took %ds." % ( time.time ( ) - start ) )

    def detect_ring_borders ( self ):
        """
        This method's goal is to detect borders, and select only the first connected set of pixels in this border.
        """
        start = time.time ( )

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
                     int ( self.wrapped.array [ row ] [ col ] ) == 0 and
                     self.noise.array [ row ] [ col ] == 0 ):
                    ring_borders_map [ row ] [ col ] = 1
        if ( numpy.sum ( ring_borders_map ) == 0 ):
            self.log.warning ( "No borders detected." )
            self.__ring_borders = numpy.ones ( shape = ring_borders_map.shape )
            return

        # color continuous ring borders with different colors
        next_color = 2
        for row in range ( max_rows ):
            self.log.debug ( "i_row = %d" % row )
            for col in range ( max_cols ):
                if ring_borders_map [ row ] [ col ] == 1:
                    borderhood = [ ( row, col ) ]
                    while ( borderhood != [ ] ):
                        self.log.debug ( "l_borderhood = %s" % str ( borderhood ) )
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
            self.log.debug ( "color_counts == { }" )
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

        # if the largest arc is too small, abort
        if max_arc_count < 20:
            self.log.error ( "max_arc_count = %d, which is too small. Assuming no border." % max_arc_count )
            self.__ring_borders = numpy.ones ( shape = ring_borders_map.shape )
            return

        self.__ring_borders = numpy.copy ( ring_borders_map )

        self.log.debug ( "detect_ring_borders() took %ds." % ( time.time ( ) - start ) )

    def find_center ( self ):
        """
        This method's goal is to to find the center by segmenting arcs and searching for the intersection of rays perpendicular to these segments.
        """
        self.detect_ring_borders ( )

        convergence_tries = 1
        bisections = [ ]
        centers = [ ]
        while ( True ):
            if ( convergence_tries > 50 ):
                self.log.warning ( "Reached threshold for center convergence using chord perpendiculars." )
                break
            if convergence_tries % 10 == 0:
                self.log.debug ( "convergence_tries = %d" % convergence_tries )
            chord_bisector_0 = self.get_random_chord_bisector ( )
            chord_bisector_1 = self.get_random_chord_bisector ( )
            while ( sympy.Line.is_parallel ( chord_bisector_0, chord_bisector_1 ) ):
                chord_bisector_0 = self.get_random_chord_bisector ( )
                chord_bisector_1 = self.get_random_chord_bisector ( )
                    
            self.log.debug ( "o_chord_bisector_0 = %s, slope = %s" % ( str ( chord_bisector_0.equation ( ) ), str ( float ( chord_bisector_0.slope.evalf ( ) ) ) ) )
            self.log.debug ( "o_chord_bisector_1 = %s, slope = %s" % ( str ( chord_bisector_1.equation ( ) ), str ( float ( chord_bisector_1.slope.evalf ( ) ) ) ) )
            bisections.append ( ( chord_bisector_0, chord_bisector_1, convergence_tries * 10 ) )

            # sometimes intesection fails because one of the bisectors ain't a GeometryEntity.
            try:
                intersection = sympy.geometry.intersection ( chord_bisector_0, chord_bisector_1 )
            except ValueError as e:
                self.log.warning ( "ValueError %s. Ignoring this intersection." % ( e ) )
                convergence_tries += 1
                continue

            if ( len ( intersection ) != 0 ):
                point_center = intersection [ 0 ]
                intersect_row = int ( point_center.x.evalf ( ) )
                intersect_col = int ( point_center.y.evalf ( ) )
                self.log.debug ( "o_point_center = %s" % str ( ( intersect_row, intersect_col ) ) )
                self.log.debug ( "i_convergence_tries * 10 = %s" % str ( convergence_tries * 10 ) )
                centers.append ( ( int ( intersect_row ), int ( intersect_col ) ) )
                sum_row = 0
                sum_col = 0
                for center in range ( len ( centers ) ):
                    sum_row +=  centers [ center ] [ 0 ]
                    sum_col +=  centers [ center ] [ 1 ]
                center = ( int ( sum_row / len ( centers ) ),
                             int ( sum_col / len ( centers ) ) )
                self.log.debug ( "center possibly at %s" % str ( center ) )
            convergence_tries += 1
            if ( convergence_tries > 10 ):
                if ( center == ( intersect_row, intersect_col ) ):
                    self.log.debug ( "t_center converged at %s" % str ( center ) )
                    break

        self.__center_row = center [ 0 ]
        self.__center_col = center [ 1 ]

    def get_center ( self ):
        """
        This method's goal is to access the calculated center coordinates. Will trigger a find if the center is yet unknown.

        Returns:

        * unnamed variable : tuple of 2 integers
            Containing the column and row of the found center.
        """
        if ( ( self.__center_row is not None ) and
             ( self.__center_col is not None ) ):
            return ( self.__center_row, self.__center_col )
        else:
            self.find_center ( )
            return ( self.__center_row, self.__center_col )

    def get_most_distant_points ( self, tl_points = [ ] ):
        """
        This method's goal is to find the pair of points that are most distant in a list of points, by calculating the distance between each possible pair.

        Parameters:

        * tl_points : list
            Containing tuples of 2 integers each.

        Returns:

        * unnamed variable : list
            Containing the first two points that are separated by the largest distance.
        """
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
        """
        This method's goal is to find a perpendicular bisector for line segments determined from two random points from the current border.

        Returns:

        * unnamed variable : sympy.Line
            Will be None if no line bisects the chord.
        """
        random_points = set ( [ ] )
        while ( len ( random_points ) < 3 ):
            self.log.debug ( "len ( random_points ) = %d" % len ( random_points ) )
            self.log.debug ( "random_points = %s" % str ( random_points ) )
            random_points . update ( [ self.get_random_point_in_border ( ) ] )
        max_distance_points = self.get_most_distant_points ( list ( random_points ) )
        point_0 = sympy.Point ( max_distance_points [ 0 ] [ 0 ], max_distance_points [ 0 ] [ 1 ] )
        point_1 = sympy.Point ( max_distance_points [ 1 ] [ 0 ], max_distance_points [ 1 ] [ 1 ] )
        self.log.debug ( "debug: point_0, point_1 = %s, %s" % ( str ( point_0 ), str ( point_1 ) ) )
        chord_segment = sympy.Segment ( point_0, point_1 )
        if ( type ( chord_segment ) is sympy.Point ):
            self.log.error ( "Segmentation created a point." )
            return None
        return chord_segment.perpendicular_bisector ( )

    def get_random_point_in_border ( self ):
        """
        This method's goal is to access a random point from the current border.
        
        Returns:
        
        * unnamed variable : tuple of 2 integers
            Corresponding to the column and row of a random position in the border.
        """
        random_row = random.randint ( 0, self.wrapped.shape [ 0 ] - 1 )
        random_col = random.randint ( 0, self.wrapped.shape [ 1 ] - 1 )
        random_color = self.__ring_borders [ random_row ] [ random_col ]
        while ( random_color == 0 ):
            random_row = random.randint ( 0, self.wrapped.shape [ 0 ] - 1 )
            random_col = random.randint ( 0, self.wrapped.shape [ 1 ] - 1 )
            random_color = self.__ring_borders [ random_row ] [ random_col ]
        return ( random_row, random_col )
