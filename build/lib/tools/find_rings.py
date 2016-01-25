# -*- coding: utf-8 -*-
"""
This module's scope is to find rings within tridimensional Fabry-Pérot spectrographs.

Example::

    >>> import tuna
    >>> raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    >>> rings = tuna.plugins.run ( "Ring center finder" ) ( data = raw )
    >>> sorted ( list ( rings.keys ( ) ) )
    ['concentric_rings', 'construction', 'gradient', 'gradients', 'lower_percentile_regions', 'ridge', 'ring_fit', 'ring_fit_parameters', 'ring_pixel_sets', 'rings', 'upper_percentile_regions']
    >>> rings [ 'rings' ]
    [(218.56306556317449, 256.97877557329144, 231.82699113784105, [0]), (219.14654183804043, 254.87497666726719, 110.1292761603854, [1]), (190.48575616356123, 248.81898301262672, 338.64377512691351, [2, 3])]
"""

__version__ = "0.1.0"
__changelog__ = {
    "0.1.0" : { "Tuna" : "0.15.0", "Change" : "Refactored to use 'data' argument of 'Ring center finder' plugin." }
    }

import copy
import IPython
import logging
import math
try:
    import mpyfit
except ImportError:
    print ( "Could not import mpyfit." )
import numpy
import random
import sympy
import time
import tuna

class rings_finder ( object ):
    """
    This class' responsibility is to find all rings contained in a data cube.

    Its constructor expects the following parameters:

    * array : numpy.ndarray
        Containing the data where ring structures are to be found.

    * plane : integer
        The index for the plane where to search for the ring.

    * ipython : object
        A reference to a ipython object, so plots produced by this module won't suppress previous plots.

    * plot_log : boolean
        If set to True, will spawn plots of intermediary products, as they are produced.
    """
    def __init__ ( self, array, plane, ipython, plot_log ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )
        self.__version__ = '0.2.4'
        self.changelog = {
            "0.2.4" : "Tuna 0.15.0 : refactored into a plugin.",
            "0.2.3" : "Tuna 0.14.0 : updated documentation to new style.",
            '0.2.2' : "Added aggregation of concentric rings into a return structure.",
            '0.2.1' : "Added ridge_thickness to the fitted circles, improving fits' speed and precision.",
            '0.2.0' : "Added function to remove lumped sets from result. Added behaviour for exhaustive search for plane containing two rings."
        }
        self.plot_log = plot_log
        self.ipython = ipython
        if self.plot_log:
            if self.ipython == None:
                self.ipython = IPython.get_ipython()
                self.ipython.magic("matplotlib qt")

        self.chosen_plane = plane
        self.ridge_threshold = 6
            
        self.array = array
        
        self.result = { }
        
    def execute ( self ):
        """
        This method's goal is to run the main algorithm:

        #. segment the image in ring and non-ring regions.

        #. Create a separate array for each individual ring.

        #. Calculate the center and the average radius.
        """
        start_time = time.time ( )
        self.segment ( ) # self.result [ 'ridge' ] contains this subresult.
        segment_time = time.time ( )
        self.separate_rings ( ) # self.result [ 'ring_pixel_sets' ] contains this subresult
        separate_time = time.time ( )
        self.fit_circles ( )
        fit_time = time.time ( )
        self.aggregate_fits ( )
        aggregate_time = time.time ( )
        self.aggregate_concentric_rings ( )
        concentric_time = time.time ( )
        self.log.debug ( "rings_finder finished. segment() {:.1f}s, separate_rings() {:.1f}s, fit_circles() {:.1f}s, aggregate_fits() {:.1f}s, aggregate_concentric_rings() {:.1f}s..".format ( segment_time - start_time, separate_time - segment_time, fit_time - separate_time, aggregate_time - fit_time, concentric_time - aggregate_time ) )
        
    def segment ( self ):
        """
        This method's goal is to segment the image in ring and non-ring regions.

        This is accomplished applying the numpy.gradient method on the input array; and then obtaining the lower percentile region (the regions in the data where the gradient is minimal) and the higher percentile region.

        The very "middle" of each ring will consist of the pixels where the gradient is in the process of changing sign; and therefore, finding these pixels (the "ridge"), is equivalent to finding the "middle" of the rings.
        """
        if len ( self.array.shape ) != 3:
            self.log.info ( "This procedure expects a 3D numpy ndarray as input." )
        
        gradients = numpy.gradient ( self.array )
        if self.plot_log:
            tuna.tools.plot ( gradients [ 0 ] [ self.chosen_plane ], "gradients [ 0 ] [ {} ]".format (
                self.chosen_plane ), self.ipython )
        self.result [ 'gradients' ] = gradients
            
        gradient = gradients [ 0 ] [ self.chosen_plane ]
        self.result [ 'gradient' ] = gradient

        self.upper_percentile = self.find_upper_percentile ( gradient )
        
        upper_percentile_value = numpy.percentile ( gradient, self.upper_percentile ) 
        upper_dep_gradient = numpy.where ( gradient > upper_percentile_value, 1, 0 )
        if self.plot_log:
            tuna.tools.plot ( upper_dep_gradient, "({}) upper_dep_gradient".format (
                self.upper_percentile ), self.ipython )
        self.result [ 'upper_percentile_regions' ] = upper_dep_gradient

        lower_percentile = tuna.tools.find_lowest_nonnull_percentile ( gradient )
        lower_percentile_value = numpy.percentile ( gradient, lower_percentile )
        lower_percentile_regions = numpy.where ( gradient < lower_percentile_value, 1, 0 )
        if self.plot_log:
            tuna.tools.plot ( lower_percentile_regions, "({}) lower_percentile_regions".format (
                lower_percentile ), self.ipython )
        self.result [ 'lower_percentile_regions' ] = lower_percentile_regions

        ridge = numpy.zeros ( shape = gradient.shape )
        for col in range ( ridge.shape [ 0 ] ):
            for row in range ( ridge.shape [ 1 ] ):
                ridge [ col ] [ row ] = self.ridgeness ( upper_dep_gradient,
                                                         lower_percentile_regions,
                                                         col, row, threshold = self.ridge_threshold )
        if self.plot_log:
            tuna.tools.plot ( ridge, "ridge ", self.ipython )
        
        self.log.debug ( "ridge found" )    
        self.result [ 'ridge' ] = ridge

    def ridgeness ( self, upper, lower, col, row, threshold = 1 ):
        """
        Returns 1 if point at col, row has threshold neighbours that is 1 in both upper and lower arrays.

        Parameters:

        * upper : numpy.ndarray
            Should contain the array with a higher percentile gradient region.

        * lower : numpy.ndarray
            Should contain the array with a lower percentile gradient region.

        * col : integer
            The column where the pixel's ridgeness is to be assessed.

        * row : integer
            The row where the pixel's ridgeness is to be assessed.

        * threshold : integer : 1
            The minimum number of neighbours in each region that a pixel must possess to be considered a "ridge" pixel.

        Returns:

        * unnamed variable : integer
            Will be 0 for pixels in the "ridge" and 0 otherwise.
        """
        neighbours = tuna.tools.get_pixel_neighbours ( ( col, row ), upper, distance_threshold = 2 )
        upper_neighbour = 0
        lower_neighbour = 0
        for neighbour in neighbours:
            if ( upper_neighbour >= threshold and
                 lower_neighbour >= threshold ):
                return 1
            if upper [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                upper_neighbour += 1
            if lower [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                lower_neighbour += 1
        if ( upper_neighbour >= threshold and
             lower_neighbour >= threshold ):
            return 1
        return 0    
            
    def fit_circles ( self ):
        """
        This method's goal is to fit circles to the data.
        """
        count = 0
        for pixel_set_tuple in self.result [ 'ring_pixel_sets' ]:
            pixel_set = pixel_set_tuple [ 0 ]
            self.log.debug ( "attempting to fit set {}".format ( count ) )

            start = time.time ( )
            minimal_point, minimal_radius = self.construct_ring_center ( pixel_set )
            self.log.debug ( "constructing_center took {:.1f}s".format ( time.time ( ) - start ) )
            if minimal_point == None or minimal_radius == None:
                self.log.error ( "Could not find center or radius." )
                minimal_point = ( 0, 0 )
                minimal_radius = 1
                
            ring_parameters, ring_fit = fit_circle ( minimal_point [ 0 ],
                                                     minimal_point [ 1 ],
                                                     minimal_radius,
                                                     pixel_set,
                                                     circle,
                                                     ridge_thickness = pixel_set_tuple [ 1 ] )
            
            self.log.debug ( "ring_parameters {} = {}".format ( count, ring_parameters ) )
            if self.plot_log:
                tuna.tools.plot ( ring_fit, "ring fit {}".format ( count ), self.ipython )
                tuna.tools.plot ( pixel_set - ring_fit, "pixel_set {} - ring_fit {}".format (
                    count, count ), self.ipython )
                tuna.tools.plot ( self.result [ 'construction' ] [ count ], "construction {}".format (
                    count ), self.ipython )
            

            try:
                self.result [ 'ring_fit' ].append ( ring_fit )
            except KeyError:
                self.result [ 'ring_fit' ] = [ ring_fit ]
            try:
                self.result [ 'ring_fit_parameters' ].append ( ring_parameters )
            except KeyError:
                self.result [ 'ring_fit_parameters' ] = [ ring_parameters ]
                
            count += 1
            
        self.log.debug ( "All sets fitted." )

    def aggregate_fits ( self ):
        """
        This method's goal is to coalesce all circles fitted in the minimum number of geometric entities.
        
        After fitting circles to pixel sets, some fits will correspond to the same ring. These must be aggregated into single results.
        """
        if 'ring_fit' not in list ( self.result.keys ( ) ):
            return
        known_centers = [ ]
        for pixel_set_index in range ( len ( self.result [ 'ring_fit' ] ) ):
            distance_threshold = min ( self.result [ 'ring_fit' ] [ pixel_set_index ].shape [ 0 ],
                                       self.result [ 'ring_fit' ] [ pixel_set_index ].shape [ 1 ] ) * 0.1
            center_is_unknown = True
            for structure in known_centers:
                center = ( structure [ 0 ], structure [ 1 ] )
                center_fit_index = structure [ 2 ] [ 0 ]
                distance = tuna.tools.calculate_distance (
                    ( self.result [ 'ring_fit_parameters' ] [ pixel_set_index ] [ 0 ],
                      self.result [ 'ring_fit_parameters' ] [ pixel_set_index ] [ 1 ] ), center )
                if distance < distance_threshold:
                    self.log.debug ( "ring_fit {} center close to ring_fit {} center".format (
                        pixel_set_index, center_fit_index ) )
                    if abs ( self.result [ 'ring_fit_parameters' ] [ pixel_set_index ] [ 2 ] - \
                             self.result [ 'ring_fit_parameters' ] [ center_fit_index ] [ 2 ] ) < distance_threshold:
                        self.log.debug ( "ring_fit {} radius similar to ring_fit {} radius".format (
                        pixel_set_index, center_fit_index ) )
                        center_is_unknown = False
                        structure [ 2 ].append ( pixel_set_index )
            if center_is_unknown:
                known_centers.append ( [ self.result [ 'ring_fit_parameters' ] [ pixel_set_index ] [ 0 ],
                                         self.result [ 'ring_fit_parameters' ] [ pixel_set_index ] [ 1 ],
                                         [ pixel_set_index ] ] )
        self.log.debug ( "known_centers = {}".format ( known_centers ) )

        rings = [ ]
        for structure in known_centers:
            center_col = 0
            center_row = 0
            radius = 0
            for entry in structure [ 2 ]:
                center_col += self.result [ 'ring_fit_parameters' ] [ entry ] [ 0 ]
                center_row += self.result [ 'ring_fit_parameters' ] [ entry ] [ 1 ]
                radius     += self.result [ 'ring_fit_parameters' ] [ entry ] [ 2 ]
            center_col /= len ( structure [ 2 ] )
            center_row /= len ( structure [ 2 ] )
            radius     /= len ( structure [ 2 ] )
        
            try:
                self.result [ 'rings' ].append ( ( center_col, center_row, radius, structure [ 2 ] ) )
            except KeyError:
                self.result [ 'rings' ] =      [ ( center_col, center_row, radius, structure [ 2 ] ) ]
        # at this point, aggregated all pixel_sets that share the same radius and center.

    def aggregate_concentric_rings ( self ):
        """
        This method's goal is to construct the geometric description of the concentric ring structure.

        The most abstract and relevant information is the following structure: ( center, radii ), where center is a tuple of floats and radii is a list of floats.

        Each spectrograph should have a single result of this kind, which is generated here and stored in self.concentric_rings.
        """

        self.log.debug ( "self.result [ 'rings' ] = {}".format ( self.result [ 'rings' ] ) )
        distance_threshold = min ( self.result [ 'ring_fit' ] [ 0 ].shape [ 0 ],
                                   self.result [ 'ring_fit' ] [ 0 ].shape [ 1 ] ) * 0.1

        concentric_rings = [ ]
        for structure in self.result [ 'rings' ]:
            struct_center = ( structure [ 0 ], structure [ 1 ] )
            struct_fits = structure [ 3 ]
            struct_radius = structure [ 2 ]

            center_is_unknown = True
            for another in concentric_rings:
                another_fits = another [ 3 ]
                if another_fits [ 0 ] == struct_fits [ 0 ]:
                    continue
                another_center = ( another [ 0 ], another [ 1 ] )
                another_radius = another [ 2 ]
                distance = tuna.tools.calculate_distance ( struct_center, another_center )
                if distance < distance_threshold:
                    center_is_unknown = False
                    another [ 3 ].append ( struct_fits [ 0 ] )
                    break
                    
            if center_is_unknown:
                concentric_rings.append ( ( struct_center [ 0 ], struct_center [ 1 ], [ struct_radius ], [ struct_fits [ 0 ] ] ) )
        self.log.debug ( "concentric_rings = {}".format ( concentric_rings ) )

        # select best structure (with the most rings, with the most pixels )
        max_num = 0
        max_structure = None
        for structure in concentric_rings:
            num_fits = len ( structure [ 3 ] )
            if num_fits > max_num:
                max_num = num_fits
                max_structure = structure
        self.log.debug ( "max_structure = {}".format ( max_structure ) )

        # generate averaged result
        averaged_col = 0
        averaged_row = 0
        averaged_num = 0
        radii = [ ]
        sets = [ ]
        for index in max_structure [ 3 ]:
            averaged_col += self.result [ 'ring_fit_parameters' ] [ index ] [ 0 ]
            averaged_row += self.result [ 'ring_fit_parameters' ] [ index ] [ 1 ]
            averaged_num += 1
            radii.append ( self.result [ 'ring_fit_parameters' ] [ index ] [ 2 ] )
            sets.append ( index )
        averaged_col /= averaged_num
        averaged_row /= averaged_num
        averaged_concentric_rings = ( ( averaged_col, averaged_row ), radii, sets )
        
        self.log.info ( "averaged_concentric_rings = {}".format ( averaged_concentric_rings ) )
        self.result [ 'concentric_rings' ] = averaged_concentric_rings
 
    def construct_ring_center ( self, pixel_set ):
        """
        This method's goal is to estimate the center and radius of a circle that is osculatory to the curve contained in the pixel_set.
        
        Parameters:

        * pixel_set : numpy.ndarray
            Bidimensional array, where each pixel has either a 0 or a 1 as value.

        Returns:

        * center : tuple of 2 floats
            Containing the column and row "coordinates" for the center.

        * radius : float 
            The radius of this center.
        """
        self.log.debug ( "construct_ring_center" )
        construction = numpy.copy ( pixel_set )
        self.log.debug ( "pixel_set copied" )

        max_pair = self.find_max_pair ( pixel_set )

        if not max_pair:
            self.log.error ( "Could not find a pixel pair!" )
            return None, None

        self.log.debug ( "max_pair = {}".format ( max_pair ) )
        color = 2
        construction [ max_pair [ 0 ] [ 0 ] ] [ max_pair [ 0 ] [ 1 ] ] = color
        construction [ max_pair [ 1 ] [ 0 ] ] [ max_pair [ 1 ] [ 1 ] ] = color

        mid_point = ( ( max_pair [ 0 ] [ 0 ] + max_pair [ 1 ] [ 0 ] ) / 2,
                      ( max_pair [ 0 ] [ 1 ] + max_pair [ 1 ] [ 1 ] ) / 2 )
        sympy_mid_point = sympy.Point ( mid_point [ 0 ], mid_point [ 1 ] )
        construction [ mid_point [ 0 ] ] [ mid_point [ 1 ] ] = color
        self.log.debug ( "mid_point = {}".format ( mid_point ) )

        chord_extreme_1 = sympy.Point ( max_pair [ 0 ] [ 0 ], max_pair [ 0 ] [ 1 ] )
        chord_extreme_2 = sympy.Point ( max_pair [ 1 ] [ 0 ], max_pair [ 1 ] [ 1 ] )
        chord_line = sympy.Line ( chord_extreme_1, chord_extreme_2 )
        self.plot_sympy_line ( construction, chord_line, color )

        color = 3
        concurrent_line = chord_line.perpendicular_line ( sympy_mid_point )
        self.plot_sympy_line ( construction, concurrent_line, color )

        color = 4
        min_pixel, concurrent_extreme_min = self.find_min_pixel ( pixel_set, concurrent_line )
        if min_pixel == None or concurrent_extreme_min == None:
            self.log.error ( "min_pixel == {}, concurrent_extreme_min = {}".format (
                min_pixel, concurrent_extreme_min ) )
            return None, None
        
        construction [ min_pixel [ 0 ] ] [ min_pixel [ 1 ] ] = color
        
        secondary_chord = sympy.Line ( chord_extreme_1, concurrent_extreme_min )
        self.plot_sympy_line ( construction, secondary_chord, color )

        secondary_angle = chord_line.angle_between ( secondary_chord )
        self.log.debug ( "secondary_angle = {} radians".format ( secondary_angle ) )

        color += 1
        thertiary_chord = secondary_chord.perpendicular_line ( chord_extreme_1 )
        self.plot_sympy_line ( construction, thertiary_chord, color )

        color += 1
        diameter_extremes_list = thertiary_chord.intersection ( concurrent_line )
        if len ( diameter_extremes_list ) == 0:
            self.log.warning ( "Could not find intersection between thertiary_chord and concurrent_line. Will attempt to recursively find another set of segments, removing one of the points from current set." )
            new_set = numpy.copy ( pixel_set )
            new_set [ max_pair [ 0 ] [ 0 ] ] [ max_pair [ 0 ] [ 1 ] ] = 0
            return self.construct_ring_center ( new_set )
        
        diameter_extreme = diameter_extremes_list [ 0 ]

        center = ( ( sympy.N ( diameter_extreme.x ) + min_pixel [ 0 ] ) / 2,
                   ( sympy.N ( diameter_extreme.y ) + min_pixel [ 1 ] ) / 2 )
        radius = tuna.tools.calculate_distance ( center, min_pixel )

        for neighbour in tuna.tools.get_pixel_neighbours (
                ( round ( center [ 0 ] ), round ( center [ 1 ] ) ), construction ):
            construction [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] = color
        
        try:
            self.result [ 'construction' ].append ( construction )
        except KeyError:
            self.result [ 'construction' ] = [ construction ]

        return center, radius

    def find_min_pixel ( self, pixel_set, line ):
        """
        This method's goal is to find the pixel that has the minimal distance to the input line.

        Parameters:

        * line : sympy.Line
            The line regarding which we want to find the closest pixel in a set.

        * pixel_set : numpy.ndarray
            The set of pixels of which we want the one closest to the input line.

        Returns:

        * min_pixel : tuple of 2 integers
            Containing the column and row coordinates for the pixel in the input set that is closest to the input line.

        * concurrent_extreme_min : sympy.Point
            The point on the input line where is the projection of the pixel in the input pixel_set that is closest to the input line.
        """
        intersection_points = [ ]
        for col in range ( pixel_set.shape [ 0 ] - 1 ):
            point_A = sympy.Point ( col, 0 )
            point_B = sympy.Point ( col, pixel_set.shape [ 1 ] - 1 )
            col_line = sympy.Line ( point_A, point_B )
            intersection = line.intersection ( col_line ) [ 0 ]
            if intersection == None:
                continue
            if isinstance ( intersection, sympy.Point ):
                x = round ( sympy.N ( intersection.x ) )
                y = round ( sympy.N ( intersection.y ) )
                if x < 0 or x >= pixel_set.shape [ 0 ]:
                    continue
                if y < 0 or y >= pixel_set.shape [ 1 ]:
                    continue
                intersection_points.append ( ( x, y ) )
                continue
            if isinstance ( intersection, sympy.Line ):
                for row in range ( pixel_set.shape [ 1 ] - 1 ):
                    intersection_points.append ( ( col, row ) )
                continue
            self.log.error ( "Intersection loop reached impossible condition!" )
        self.log.debug ( "len ( intersection_points ) = {}".format ( len ( intersection_points ) ) )

        pixel_set_intersections = [ ]
        for intersection in intersection_points:
            if pixel_set [ intersection [ 0 ] ] [ intersection [ 1 ] ] == 1:
                pixel_set_intersections.append ( intersection )
        if len ( pixel_set_intersections ) == 0:
            self.log.error ( "len ( pixel_set_intersections ) == 0, falling back to whole pixel_set" )
            for col in range ( pixel_set.shape [ 0 ] ):
                for row in range ( pixel_set.shape [ 1 ] ):
                    if pixel_set [ col ] [ row ] == 1:
                        pixel_set_intersections.append ( ( col, row ) )
        self.log.debug ( "len ( pixel_set_intersections ) = {}".format ( len ( pixel_set_intersections ) ) )

        min_distance = float ( "inf" )
        min_pixel = None
        concurrent_extreme_min = None
        for pixel in pixel_set_intersections:
            sympy_point = sympy.Point ( pixel [ 0 ], pixel [ 1 ] )
            self.log.debug ( "sympy_point.x = {}, sympy_point.y = {}".format ( sympy.N ( sympy_point.x ),
                                                                              sympy.N ( sympy_point.y ) ) )
            projection = line.projection ( sympy_point )
            self.log.debug ( "projection.x = {}, projection.y = {}".format ( sympy.N ( projection.x ),
                                                                            sympy.N ( projection.y ) ) )
            distance = tuna.tools.calculate_distance ( ( round ( pixel [ 0 ] ),
                                                         round ( pixel [ 1 ] ) ),
                                                       ( sympy.N ( projection.x ),
                                                         sympy.N ( projection.y ) ) )
            self.log.debug ( "distance = {}".format ( distance ) )
            if distance <= min_distance:
                min_distance = distance
                min_pixel = ( round ( pixel [ 0 ] ), round ( pixel [ 1 ] ) )
                concurrent_extreme_min = ( sympy.N ( projection.x ), sympy.N ( projection.y ) )
                self.log.debug ( "current min_distance = {}, min_pixel = {}, concurrent_extreme_min = {}".format (
                    min_distance, min_pixel, concurrent_extreme_min ) )
        self.log.debug ( "final min_distance = {}, min_pixel = {}, concurrent_extreme_min = {}".format (
            min_distance, min_pixel, concurrent_extreme_min ) )
        return ( min_pixel, concurrent_extreme_min )
    
    def find_max_pair ( self, pixel_set ):
        """
        This method's goal is to find the two pixels in the input set that are maximally distant to each other.

        Parameters:

        * pixel_set : numpy.ndarray
            An array where zeros indicate lack of points, and ones indicate presence of points.

        Returns:

        * max_pair : tuple of 2 tuples, of 2 integers each
            Contains the coordinates of the two points maximally distant.
        """
        pixels = [ ]
        for col in range ( pixel_set.shape [ 0 ] ):
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] == 1:
                    pixels.append ( ( col, row ) )
        self.log.debug ( "pixels list populated with {} pixels".format ( len ( pixels ) ) )

        if len ( pixels ) > 5000:
            old_pixels = copy.copy ( pixels )
            pixels = [ ]
            for count in range ( 5000 ):
                index = random.randint ( 0, len ( old_pixels ) )
                pixels.append ( old_pixels [ index ] )
            self.log.debug ( "pixels list downgraded to {} pixels.".format ( len ( pixels ) ) )
        
        max_distance = 0
        max_pair = None
        for pixel in pixels:
            for other in pixels:
                distance = tuna.tools.calculate_distance ( pixel, other )
                if distance >= max_distance:
                    max_distance = distance
                    max_pair = ( pixel, other )
        return max_pair
        
    def find_upper_percentile ( self, gradient ):
        """
        Tries to find the maximum percentile that contains at least 10 % of the pixels.
        """
        full = gradient.shape [ 0 ] * gradient.shape [ 1 ]
        attempt = 99
        ratio = 0
        while ( ratio < 0.1 ):
            attempt_value = numpy.percentile ( gradient, attempt )
            ratio = numpy.sum ( numpy.where ( gradient > attempt_value, 1, 0 ) ) / full
            attempt -= 1
            if attempt < 3:
                break
        self.log.debug ( "find_upper_percentile: {}".format ( attempt ) )
        return attempt
        
    def plot_sympy_line ( self, array, sympy_line, color ):
        """
        This method's goal is to add a line to an array.
        It expects to receive an array where pixels that have points have non-null value.
        From a line specified as a Sympy object, it will color pixels in the array using the value for color.

        Parameters:

        * array : numpy.ndarray
            Containing the data where the line will be drawn in-place.

        * sympy_line : sympy.Line
            An object describing the geometry of the line to be drawn.

        * color : integer
            The value to attribute to each pixel in the input array that is crossed by the geometric input line.
        """
        for col in range ( array.shape [ 0 ] ):
            sympy_point_0 = sympy.Point ( col, 0 )
            sympy_point_1 = sympy.Point ( col, array.shape [ 1 ] - 1 )
            concurrent = sympy.Line ( sympy_point_0, sympy_point_1 )
            if sympy.Line.is_parallel ( concurrent, sympy_line ):
                if sympy_line.contains ( sympy_point_0 ):
                    self.log.warning ( "Line to plot parallel ({}) to col axis.".format ( sympy_point_0.x ) )
                    for row in range ( array.shape [ 1 ] ):
                        array [ sympy_point_0.x ] [ row ] = color
                    return
                continue
            intersections_list = sympy_line.intersection ( concurrent )
            intersection = intersections_list [ 0 ]
            if ( round ( intersection.y ) >= 0 and
                 round ( intersection.y ) < array.shape [ 1 ] ):
                array [ round ( intersection.x ) ] [ round ( intersection.y ) ] = color
            
    def separate_rings ( self ):
        """
        This method's goal is to create distinct array objects for each disjoint pixel set in the current self.result [ 'ridge' ] array.
        """
        array = self.result [ 'ridge' ]
        visited = numpy.zeros ( shape = array.shape )
        connected_pixels_sets = [ ]
        for col in range ( array.shape [ 0 ] ):
            for row in range ( array.shape [ 1 ] ):
                if visited [ col ] [ row ] == 1:
                    continue
                if array [ col ] [ row ] == 1:
                    to_visit = [ ( col, row ) ]
                    region = [ ]
                    while ( len ( to_visit ) > 0 ):
                        here = to_visit.pop ( )
                        visited [ here [ 0 ] ] [ here [ 1 ] ] = 1
                        region.append ( here )
                        neighbours = tuna.tools.get_pixel_neighbours ( here, array )
                        for neighbour in neighbours:
                            if visited [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                                continue
                            if array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 0:
                                continue
                            to_visit.append ( neighbour )
                    connected_pixels_sets.append ( region )

        self.log.debug ( "len connected_pixels_sets = {}".format ( len ( connected_pixels_sets ) ) )

        shape_len = array.shape [ 0 ] * array.shape [ 1 ]
        min_len = math.ceil ( array.shape [ 0 ] * array.shape [ 1 ] * 0.1 )
        min_threshold = math.ceil ( array.shape [ 0 ] * array.shape [ 1 ] * 0.001 )
        ring_pixel_sets = [ ]
        old_len = 0
        while ( len ( ring_pixel_sets ) < len ( connected_pixels_sets ) ):
            min_len *= 0.9
            self.log.debug ( "min_len for a pixel set = {:.0f}".format ( min_len ) )
            if min_len < min_threshold:
                self.log.debug ( "min_len below min_threshold" )
                break
            ring_pixel_sets = [ ]
            for pixels_set in connected_pixels_sets:
                if len ( pixels_set ) < min_len:
                    continue
                set_array = numpy.zeros ( shape = array.shape )
                for pixel in pixels_set:
                    set_array [ pixel [ 0 ] ] [ pixel [ 1 ] ] = 1
                ring_pixel_sets.append ( set_array )
            if len ( ring_pixel_sets ) == len ( connected_pixels_sets ):
                break

        ring_pixel_sets = self.remove_lumped_pixel_sets ( ring_pixel_sets )
            
        self.result [ 'ring_pixel_sets' ] = ring_pixel_sets
        self.log.debug ( "{} rings found.".format ( len ( self.result [ 'ring_pixel_sets' ] ) ) )
        if self.plot_log:
            count = 0
            for pixel_set in self.result [ 'ring_pixel_sets' ]:
                tuna.tools.plot ( pixel_set [ 0 ], "pixel_set {}".format ( count ), self.ipython )
                count += 1

    def remove_lumped_pixel_sets ( self, pixel_sets ):
        """
        For some cubes, in some planes, the central region has many pixels that do not belong to a ring, but are identified as part of the ridge. This is possibly due to a "nascent" ring in that plane.
        This function identifies such regions and removes them from the returned set.

        Parameters:

        * pixel_sets : list of numpy.ndarrays
            Containing disjoint pixel sets.
        """

        result = [ ]
        for pixel_set in pixel_sets:
            # test: each column and row should have either none, one * thickness or two * thickness pixels in the set.
            num_good_cols = 0
            num_cols = 0
            latest_thickness = 0
            average_thickness = 0
            for col in range ( pixel_set.shape [ 0 ] ):
                per_col_pixels = ( numpy.sum ( pixel_set [ col ] ) )
                if per_col_pixels == 0:
                    continue
                num_cols += 1
                if latest_thickness == 0:
                    num_good_cols += 1
                    latest_thickness = per_col_pixels
                    continue
                ratio = round ( latest_thickness / per_col_pixels )
                latest_thickness = per_col_pixels
                average_thickness += latest_thickness
                if ratio == 0.5 or ratio == 1 or ratio == 2:
                    num_good_cols +=1
                    continue
            good_cols_ratio = num_good_cols / num_cols
            average_thickness /= num_good_cols * 4
            self.log.debug ( "good_cols_ratio = {:.2f}".format ( good_cols_ratio ) )
            self.log.debug ( "average_thickness = {:.2f}".format ( average_thickness ) )
            if good_cols_ratio > 0.9:
                self.log.debug ( "pixel set probably contains a circle or arc." )
                result.append ( ( pixel_set, average_thickness ) )
                continue              
        return result
            
def circle ( center, radius, thickness, shape ):
    """
    This function's goal is to generate an array with the value 1 for every pixel that is "thickness" distant to a circle with the input radius and center.

    Parameters:

    * center : tuple of two floats
        Containing the coordinates for the circle center.

    * radius : float
        
    * thickness : float
        Each pixel's distance to the center is calculated; if this distance minus the radius is less than or equal to the thickness, then the pixel receives the value 1.

    * shape : tuple of integers
        The dimensions for the resulting array.
    """
    log = logging.getLogger ( __name__ )
    log.debug ( "center = ( {:.5f}, {:.5f} ), radius = {:.5f}".format (
        center [ 0 ], center [ 1 ], radius, shape ) )
    
    distances = numpy.zeros ( shape = shape )
    for col in range ( shape [ 0 ] ):
        for row in range ( shape [ 1 ] ):
            center_distance = tuna.tools.calculate_distance ( center, ( col, row ) )
            if abs ( center_distance - radius ) <= thickness:
                distances [ col ] [ row ] = 1

    return distances

def least_circle ( p, args ):
    """
    This function's goal is to wrap around a call to the function circle, so that it is called according to mpyfit's API.

    Parameters:

    * p : tuple
        Contains parameters used to call the function.

    * args : tuple
        Contains parameters used to call the function.

    Returns:

    * residue.flatten ( ) : numpy.ndarray
        With the fitted circle.
    """
    log = logging.getLogger ( __name__ )
    center_col, center_row, radius, thickness = p
    shape, data, function = args
    
    try:
        calculated_circle = function ( ( center_col,
                                         center_row ),
                                       radius,
                                       thickness,
                                       shape )
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )

    try:
        residue = calculated_circle - data
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )

    log.debug ( "residue = %f" % numpy.sum ( numpy.abs ( residue ) ) )
    return ( residue.flatten ( ) )

def fit_circle ( center_col, center_row, radius, data, function, ridge_thickness = 1 ):
    """
    This function's goal is to fit a circle to the input data.

    Parameters:

    * center_col : float 
        The column coordinate of the center.

    * center_row : float
        The row coordinate of the center.

    * radius : float

    * data : numpy.ndarray

    * function : object
        A reference to the function to be used for fitting.

    * ridge_thickness : float : 1
        The thickness of the ring to be fitted to the data.
    """
    log = logging.getLogger ( __name__ )

    parameters = ( float ( center_col ),
                   float ( center_row ),
                   float ( radius ),
                   float ( ridge_thickness ) )
    
    # Constraints on parameters
    parinfo = [ ]
    parbase = { 'fixed'  : False,
                'step'   : 2 }
    parinfo.append ( parbase )
    parbase = { 'fixed'  : False,
                'step'   : 2 }
    parinfo.append ( parbase )
    parbase = { 'fixed'  : False,
                'step'   : 2 }
    parinfo.append ( parbase )
    # ridge_thickness
    parbase = { 'fixed'  : False,
                'step'   : 0.1 }
    parinfo.append ( parbase )
    
    for entry in parinfo:
        log.debug ( "parinfo = %s" % str ( entry ) )
            
    try:
        log.debug ( "fit_circle input parameters = {}".format ( parameters ) )
        fit_parameters, fit_result = mpyfit.fit ( least_circle,
                                                  parameters,
                                                  args = ( data.shape, data, function ),
                                                  parinfo = parinfo,
                                                  xtol = 1e-1 )
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )
        raise ( e )

    log.debug ( "fit_circle result = {}".format ( fit_result ) )

    
    return fit_parameters, function (
        ( fit_parameters [ 0 ], fit_parameters [ 1 ] ), fit_parameters [ 2 ], ridge_thickness, data.shape )

def find_rings ( data : numpy.ndarray,
                 min_rings : int = 1,
                 plane : int = None,
                 ipython : object = None,
                 plot_log : bool = False ) -> dict:
    """
    Attempts to find rings contained in a 3D numpy ndarray input.

    Parameters:

    * data : numpy.ndarray 
        A tridimensional spectrogram. This parameter can also be a Tuna can.

    * min_rings : integer
        This is the minimal number of rings expected to be found.

    * plane : integer : None
        This is the index in the cube for the spectrograph whose rings the user wants. If no plane is specified, all planes will be search (from 0 onwards) until at least two rings are found in a plane.

    * ipython : object : None
        Contains a reference to the ipython object, in case it exists.

    * plot_log : boolean : False
        Flags whether to output plots of the intermediary products. Even when not plotting, all numpy arrays are accessible in the result structure.

    Returns:

    * dict
        With the following keys: 

        * 'array' : 2D numpy.ndarray where pixels in the ring have value 1 and other pixels have value 0.
        * 'center' : a tuple of 2 floats, where the first is the column and the second is the row of the most probable locations for the center of that ring.
        * 'radius' : a float with the average value of the distance of the ring pixels to its center.
        * 'construction' : a list of numpy arrays containing the geometric construction that led to the estimated center and radius used in the fit.
        * 'pixel_set' : a list of numpy arrays containing the segmented pixel sets corresponding to each identified ring.
    """
    __version__ = "0.1.0"
    __changelog__ = {
        "0.1.0" : { "Tuna" : "0.15.0", "Change" : "Changed name of input variable to data." }
        }
    
    log = logging.getLogger ( __name__ )
    
    if isinstance ( data, tuna.io.can ):
        effective_array = data.array
        log.debug ( "Using can's array as input." )
    else:
        effective_array = data

    if plane != None:
        finder = rings_finder ( effective_array, plane, ipython, plot_log )
        finder.execute ( )
        return finder.result

    # no plane was specified
    best_so_far = None
    for effective_plane in range ( effective_array.shape [ 0 ] ):
        finder = rings_finder ( effective_array, effective_plane, ipython, plot_log )
        finder.execute ( )
        if 'concentric_rings' not in list ( finder.result.keys ( ) ):
            self.log.warning ( "No concentric rings on plane {}.".format ( effective_plane ) )
            continue
        log.debug ( "concentric_rings [ 1 ] = {}".format ( finder.result [ 'concentric_rings' ] [ 1 ] ) )
        if len ( finder.result [ 'concentric_rings' ] [ 1 ] ) >= min_rings:
            return finder.result
        elif best_so_far == None:
            best_so_far = finder.result
        elif len ( finder.result [ 'concentric_rings' ] [ 1 ] ) > len ( best_so_far [ 'concentric_rings' ] [ 1 ] ):
            best_so_far = finder.result

    self.log.warning ( "Could not find a plane with two rings on the cube!" )

    if best_so_far != None:
        self.log.warning ( "Returning single ring result." )
    return best_so_far
