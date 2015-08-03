"""
The scope of this module is to find rings within 3D FP spectrographs.
"""

import IPython
import logging
import math
import mpyfit
import numpy
import sympy
import tuna

class rings_finder ( object ):
    """
    The responsibility of this class is to find all rings contained in a data cube.
    """
    def __init__ ( self, array, plane ):
        self.log = logging.getLogger ( __name__ )
        self.__version__ = '0.1.3'
        self.changelog = {
            '0.1.3' : "Made plane a parameter of init.",
            '0.1.2' : "Added construct_ring_center function.",
            '0.1.1' : "check_is_circle now returns False if there is a pixel with less than two neighbours in the ring",
            '0.1.0' : "Initial version." }
        self.plot_log = True
        if self.plot_log:
            self.ipython = IPython.get_ipython()
            self.ipython.magic("matplotlib qt")

        self.chosen_plane = plane
        self.ridge_threshold = 2
        self.upper_percentile = 90
            
        self.array = array
        
        self.result = { }
        
    def execute ( self ):
        """
        1. segment the image in ring and non-ring regions.
        2. Create a separate array for each individual ring.
        3. Calculate the center and the average radius.
        """
        self.segment ( ) # self.result [ 'ridge' ] contains this subresult.
        self.get_statistics ( ) # self.result [ 'max_number_of_rings' ] contains this subresult
        self.separate_rings ( ) # self.result [ 'ring_pixel_sets' ] contains this subresult
        self.fit_circles ( )
        self.log.debug ( "rings_finder finished." )
        
    def segment ( self ):
        if len ( self.array.shape ) != 3:
            self.log.info ( "This procedure expects a 3D numpy ndarray as input." )
        
        gradients = numpy.gradient ( self.array )
        if self.plot_log:
            tuna.tools.plot ( gradients [ 0 ] [ self.chosen_plane ], "gradients [ 0 ] [ {} ]".format (
                self.chosen_plane ), self.ipython )
        self.result [ 'gradients' ] = gradients
            
        gradient = gradients [ 0 ] [ self.chosen_plane ]
        self.result [ 'gradient' ] = gradient
            
        upper_percentile_value = numpy.percentile ( gradient, self.upper_percentile ) 
        upper_dep_gradient = numpy.where ( gradient > upper_percentile_value, 1, 0 )
        if self.plot_log:
            tuna.tools.plot ( upper_dep_gradient, "({}) upper_dep_gradient".format (
                self.upper_percentile ), self.ipython )

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
        """
        neighbours = tuna.tools.get_pixel_neighbours ( ( col, row ), upper )
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
            
    def get_statistics ( self ):
        array = self.result [ 'ridge' ]
        max_col_crossings = 0
        max_col_cross = -1
        for col in range ( array.shape [ 0 ] ):
            border_latest = 0
            border_crossings = 0
            for row in range ( array.shape [ 1 ] ):
                if array [ col ] [ row ] == 1:
                    if border_latest == 0:
                        border_crossings += 1
                        if border_crossings > max_col_crossings:
                            max_col_crossings = border_crossings
                            max_col_cross = col                        
                        border_latest = 1
                else:
                    border_latest = 0
        self.log.debug ( "row {} has {} max border crossings.".format ( max_col_cross, max_col_crossings ) )
        max_row_crossings = 0
        for row in range ( array.shape [ 1 ] ):
            border_latest = 0
            border_crossings = 0
            for col in range ( array.shape [ 0 ] ):
                if array [ col ] [ row ] == 1:
                    if border_latest == 0:
                        border_crossings += 1
                        if border_crossings > max_row_crossings:
                            max_row_crossings = border_crossings
                            max_row_cross = row
                        border_latest = 1
                else:
                    border_latest = 0
        self.log.debug ( "col {} has {} max border crossings.".format ( max_row_cross, max_row_crossings ) )
        max_crossings = max ( max_row_crossings, max_col_crossings )

        max_number_of_rings = max_crossings # this will be the case if we have a spectrograph containing only the "corner" of all its rings.
        
        self.log.debug ( "max_number_of_rings = {}".format ( max_number_of_rings ) )
        self.result [ 'max_number_of_rings' ] = max_number_of_rings

    def fit_circles ( self ):
        count = 0
        for pixel_set in self.result [ 'ring_pixel_sets' ]:
            self.log.debug ( "attempting to fit set {}".format ( count ) )

            #mountain_fit = mountain ( pixel_set, factor = 0.99, minimum_target = 1e-10 )
            #try:
            #    self.result [ 'mountain_fit' ].append ( mountain_fit )
            #except KeyError:
            #    self.result [ 'mountain_fit' ] = [ mountain_fit ]
            #if self.plot_log:
            #    tuna.tools.plot ( mountain_fit, "mountain_fit {}".format ( count ), self.ipython )

            #is_ring = self.check_set_is_ring ( pixel_set )
            #self.log.debug ( "check_set_is_ring = {}".format ( is_ring ) )
            #if is_ring:
            #    minimal_point, minimal_radius = self.estimate_for_full_ring ( pixel_set )
            #else:
            #    minimal_point, minimal_radius = self.estimate_center_from_curve ( pixel_set )

            minimal_point, minimal_radius = self.construct_ring_center ( pixel_set )
                
            ring_parameters, ring_fit = fit_circle ( minimal_point [ 0 ],
                                                     minimal_point [ 1 ],
                                                     minimal_radius,
                                                     #mountain_fit,
                                                     pixel_set,
                                                     circle )
                                                     #mountain_circle )
            
            self.log.info ( "ring_parameters {} = {}".format ( count, ring_parameters ) )
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

    def estimate_center_from_curve ( self, pixel_set ):
        pixels = [ ]
        for col in range ( pixel_set.shape [ 0 ] ):
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] == 1:
                    pixels.append ( ( col, row ) )
        
        max_distance = 0
        max_pair = None
        for pixel in pixels:
            for other in pixels:
                distance = tuna.tools.calculate_distance ( pixel, other )
                if distance >= max_distance:
                    max_distance = distance
                    max_pair = ( pixel, other )

        if not max_pair:
            self.log.error ( "Could not find a pixel pair!" )
            return None, None

        self.log.debug ( "max_pair = {}".format ( max_pair ) )

        mid_point = ( ( max_pair [ 0 ] [ 0 ] + max_pair [ 1 ] [ 0 ] ) / 2,
                      ( max_pair [ 0 ] [ 1 ] + max_pair [ 1 ] [ 1 ] ) / 2 )

        self.log.debug ( "mid_point = {}".format ( mid_point ) )
        
        min_distance = math.sqrt ( pixel_set.shape [ 0 ] ** 2 + pixel_set.shape [ 1 ] ** 2 )
        for pixel in pixels:
            distance = tuna.tools.calculate_distance ( pixel, mid_point )
            if distance <= min_distance:
                min_distance = distance
                min_pixel = pixel

        self.log.debug ( "min_distance = {}".format ( min_distance ) )
        ratio = min_distance / max_distance
        self.log.debug ( "ratio = {}".format ( ratio ) )

        if ratio > 0.4:
            center = mid_point
            radius = min_distance
            self.log.debug ( "Estimated center = ( {:.5f}, {:.5f} ), radius = {:.5f}".format (
                center [ 0 ], center [ 1 ], radius ) )
            return center, radius
        #elif ratio > 0.2:
        #    self.log.debug ( "Partial ring is too large for this algorithm. Using full ring algorithm instead." )
        #    #return self.estimate_for_full_ring ( pixel_set )

        dir_vector = ( - min_pixel [ 0 ] + mid_point [ 0 ], - min_pixel [ 1 ] + mid_point [ 1 ] )
        dir_vector_normalizer = math.sqrt ( dir_vector [ 0 ] ** 2 + dir_vector [ 1 ] ** 2 )
        dir_vector = ( dir_vector [ 0 ] / dir_vector_normalizer, dir_vector [ 1 ] / dir_vector_normalizer )
        self.log.debug ( "dir_vector = {}".format ( dir_vector ) )
        
        radius = max_distance * math.sqrt ( 2 ) / 2 + min_distance
        center = ( min_pixel [ 0 ] + radius * dir_vector [ 0 ],
                   min_pixel [ 1 ] + radius * dir_vector [ 1 ] )
            
        self.log.debug ( "Estimated center = ( {:.5f}, {:.5f} ), radius = {:.5f}".format (
            center [ 0 ], center [ 1 ], radius ) )
        
        return center, radius

    def construct_ring_center ( self, pixel_set ):
        construction = numpy.copy ( pixel_set )
        pixels = [ ]
        for col in range ( pixel_set.shape [ 0 ] ):
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] == 1:
                    pixels.append ( ( col, row ) )
        
        max_distance = 0
        max_pair = None
        for pixel in pixels:
            for other in pixels:
                distance = tuna.tools.calculate_distance ( pixel, other )
                if distance >= max_distance:
                    max_distance = distance
                    max_pair = ( pixel, other )

        if not max_pair:
            self.log.error ( "Could not find a pixel pair!" )
            return None, None

        self.log.debug ( "max_pair = {}".format ( max_pair ) )
        color = 2
        construction [ max_pair [ 0 ] [ 0 ] ] [ max_pair [ 0 ] [ 1 ] ] = color
        construction [ max_pair [ 1 ] [ 0 ] ] [ max_pair [ 1 ] [ 1 ] ] = color

        mid_point = ( ( max_pair [ 0 ] [ 0 ] + max_pair [ 1 ] [ 0 ] ) / 2,
                      ( max_pair [ 0 ] [ 1 ] + max_pair [ 1 ] [ 1 ] ) / 2 )
        construction [ mid_point [ 0 ] ] [ mid_point [ 1 ] ] = color
        
        self.log.debug ( "mid_point = {}".format ( mid_point ) )
        
        min_distance = math.sqrt ( pixel_set.shape [ 0 ] ** 2 + pixel_set.shape [ 1 ] ** 2 )
        for pixel in pixels:
            distance = tuna.tools.calculate_distance ( pixel, mid_point )
            if distance <= min_distance:
                min_distance = distance
                min_pixel = pixel
        construction [ min_pixel [ 0 ] ] [ min_pixel [ 1 ] ] = color
        
        self.log.debug ( "min_distance = {}".format ( min_distance ) )
        self.log.debug ( "min_pixel = {}".format ( min_pixel ) )
        ratio = min_distance / max_distance
        self.log.debug ( "ratio = {}".format ( ratio ) )

        chord_extreme_1 = sympy.Point ( max_pair [ 0 ] [ 0 ], max_pair [ 0 ] [ 1 ] )
        chord_extreme_2 = sympy.Point ( max_pair [ 1 ] [ 0 ], max_pair [ 1 ] [ 1 ] )
        chord_line = sympy.Line ( chord_extreme_1, chord_extreme_2 )
        self.plot_sympy_line ( construction, chord_line, color )

        concurrent_extreme_min = sympy.Point ( min_pixel [ 0 ], min_pixel [ 1 ] )
        concurrent_extreme_mid = sympy.Point ( mid_point [ 0 ], mid_point [ 1 ] )
        concurrent_line = sympy.Line ( concurrent_extreme_min, concurrent_extreme_mid )
        self.plot_sympy_line ( construction, concurrent_line, color )

        secondary_chord = sympy.Line ( chord_extreme_1, concurrent_extreme_min )
        self.plot_sympy_line ( construction, secondary_chord, color )

        secondary_angle = chord_line.angle_between ( secondary_chord )
        self.log.debug ( "secondary_angle = {} radians".format ( secondary_angle ) )

        thertiary_chord = secondary_chord.perpendicular_line ( chord_extreme_1 )
        self.plot_sympy_line ( construction, thertiary_chord, color )

        diameter_extremes_list = thertiary_chord.intersection ( concurrent_line )
        diameter_extreme = diameter_extremes_list [ 0 ]

        center = ( ( sympy.N ( diameter_extreme.x ) + min_pixel [ 0 ] ) / 2,
                   ( sympy.N ( diameter_extreme.y ) + min_pixel [ 1 ] ) / 2 )
        radius = tuna.tools.calculate_distance ( center, min_pixel )

        for neighbour in tuna.tools.get_pixel_neighbours ( center, construction ):
            construction [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] = color
        
        try:
            self.result [ 'construction' ].append ( construction )
        except KeyError:
            self.result [ 'construction' ] = [ construction ]

        return center, radius

    def plot_sympy_line ( self, array, sympy_line, color ):
        for col in range ( array.shape [ 0 ] ):
            sympy_point_0 = sympy.Point ( col, 0 )
            sympy_point_1 = sympy.Point ( col, array.shape [ 1 ] - 1 )
            concurrent = sympy.Line ( sympy_point_0, sympy_point_1 )
            if sympy.Line.is_parallel ( concurrent, sympy_line ):
                self.log.warning ( "Line to plot parallel to 0 axis, aborting plot." )
                return
            intersections_list = sympy_line.intersection ( concurrent )
            intersection = intersections_list [ 0 ]
            if ( round ( intersection.y ) >= 0 and
                 round ( intersection.y ) < array.shape [ 1 ] ):
                array [ round ( intersection.x ) ] [ round ( intersection.y ) ] = color
        
            
    def estimate_for_full_ring ( self, pixel_set ):
        pixels = 0
        center_col = 0
        center_row = 0
        for col in range ( pixel_set.shape [ 0 ] ):
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] == 1:
                    pixels += 1
                    center_col += col
                    center_row += row
        center_col /= pixels
        center_row /= pixels
        center = ( center_col, center_row )
        self.log.debug ( "center = {}".format ( center ) )
        radius = self.estimate_minimal_radius ( pixel_set, center )
        self.log.debug ( "radius = {:.5f}".format ( radius ) )
        return center, radius
    
    def check_set_is_ring ( self, pixel_set ):
        for col in range ( pixel_set.shape [ 0 ] ):
            for row in [ 0, pixel_set.shape [ 1 ] - 1 ]:
                if pixel_set [ col ] [ row ] != 0:
                    return False
        for col in [ 0, pixel_set.shape [ 0 ] - 1 ]:
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] != 0:
                    return False

        for col in range ( pixel_set.shape [ 0 ] ):
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] != 1:
                    continue
                neighbours = tuna.tools.get_pixel_neighbours ( ( col, row ), pixel_set )
                adjacent = 0
                for neighbour in neighbours:
                    if pixel_set [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                        adjacent += 1
                if adjacent < 2:
                    return False
                
        return True

    def estimate_minimal_radius ( self, pixel_set, center ):
        western_point = ( pixel_set.shape [ 0 ] - 1, 0 )
        eastern_point = ( 0, 0 )
        northern_point = ( 0, pixel_set.shape [ 1 ] - 1 )
        southern_point = ( 0, 0 )
        for col in range ( pixel_set.shape [ 0 ] ):
            for row in range ( pixel_set.shape [ 1 ] ):
                if pixel_set [ col ] [ row ] != 1:
                    continue
                if col <= western_point [ 0 ]:
                    western_point = ( col, row )
                if col >= eastern_point [ 0 ]:
                    eastern_point = ( col, row )
                if row <= northern_point [ 1 ]:
                    northern_point = ( col, row )
                if row >= southern_point [ 1 ]:
                    southern_point = ( col, row )
                    points = [ western_point, eastern_point, northern_point, southern_point ]
        self.log.debug ( "cardinal points: {}".format ( points ) )
        distances = [ ]
        for point in points:
            distances.append ( tuna.tools.calculate_distance ( point, center ) )
        self.log.debug ( "cardinal distances to center: {:.5f}, {:.5f}, {:.5f}, {:.5f}.".format (
            distances [ 0 ], distances [ 1 ], distances [ 2 ], distances [ 3 ] ) )
        radius = max ( distances )
        self.log.debug ( "radius: {}".format ( radius ) )
        return radius 
    
    def separate_rings ( self ):
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

        pixels_set_lengths = [ ]
        for pixels_set in connected_pixels_sets:
            pixels_set_lengths.append ( len ( pixels_set ) )
        sorted_pixels_set_lengths = sorted ( pixels_set_lengths )
        shortest = sorted_pixels_set_lengths [ - ( self.result [ 'max_number_of_rings' ] - 1 ) ]
        longest = sorted_pixels_set_lengths [ - 1 ]

        for pixels_set in connected_pixels_sets:
            if len ( pixels_set ) < shortest:
                continue
            if len ( pixels_set ) < 10:
                continue
            if len ( pixels_set ) < longest * 0.1:
                continue
            set_array = numpy.zeros ( shape = array.shape )
            for pixel in pixels_set:
                set_array [ pixel [ 0 ] ] [ pixel [ 1 ] ] = 1
            try:
                self.result [ 'ring_pixel_sets' ].append ( set_array )
            except KeyError:
                self.result [ 'ring_pixel_sets' ] = [ set_array ]

        self.log.debug ( "pixels_sets found" )
        if self.plot_log:
            count = 0
            for pixel_set in self.result [ 'ring_pixel_sets' ]:
                tuna.tools.plot ( pixel_set, "pixel_set {}".format ( count ), self.ipython )
                count += 1
            
def find_rings ( array ):
    """
    Attempts to find rings contained in a 3D numpy ndarray input.
    Returns a list of dicts, with the following keys:
    'array'  : 2D numpy.ndarray where pixels in the ring have value 1 and other pixels have value 0.
    'center' : a tuple of 2 floats, where the first is the column and the second is the row of the most probable locations for the center of that ring.
    'plane'  : A non-negative integer that corresponds to the index of the plane where this ring is in the original cube.
    'radius' : a float with the average value of the distance of the ring pixels to its center.
    """

    finder = rings_finder ( array )
    finder.execute ( )
    return finder.result

def circle ( center, radius, shape ):
    log = logging.getLogger ( __name__ )
    log.debug ( "center = ( {:.5f}, {:.5f} ), radius = {:.5f}".format (
        center [ 0 ], center [ 1 ], radius, shape ) )
    
    distances = numpy.zeros ( shape = shape )
    for col in range ( shape [ 0 ] ):
        for row in range ( shape [ 1 ] ):
            center_distance = tuna.tools.calculate_distance ( center, ( col, row ) )
            if abs ( center_distance - radius ) < 1:
                distances [ col ] [ row ] = 1

    #log.debug ( "returning result" )
    return distances

def mountain ( array, factor = 0.9, minimum_target = 0.5 ):
    log = logging.getLogger ( __name__ )
    log.debug ( "growing mountain with factor = {}, minimum_target = {}".format ( factor, minimum_target ) )
    target = 1
    result = numpy.copy ( array )
    mountain_pixels = 0
    total_pixels = array.shape [ 0 ] * array.shape [ 1 ]
    while ( target > minimum_target and mountain_pixels != total_pixels ):
        for col in range ( result.shape [ 0 ] ):
            for row in range ( result.shape [ 1 ] ):
                #if ( result [ col ] [ row ] == target or
                #     col == 0 or row == 0 or
                #     col == result.shape [ 0 ] - 1 or
                #     row == result.shape [ 1 ] - 1 ):
                if ( result [ col ] [ row ] == target ):
                    neighbours = tuna.tools.get_pixel_neighbours ( ( col, row ), result )
                    for neighbour in neighbours:
                        if result [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 0:
                            result [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] = target * factor
        target *= factor
        mountain_pixels = numpy.sum ( numpy.where ( result == 0, 0, 1 ) )
    log.debug ( "mountain covers {:.2f}% of array".format ( 100 * mountain_pixels / total_pixels ) )

    return result

def mountain_circle ( center, radius, shape ):
    log = logging.getLogger ( __name__ )
    fitted_circle = circle ( center, radius, shape )
    fitted_mountain = mountain ( fitted_circle )
    #log.debug ( "mountain_circle returning fitted_mountain" )
    return fitted_mountain

def least_circle ( p, args ):
    log = logging.getLogger ( __name__ )
    #log.debug ( "least_circle" )
    
    center_col, center_row, radius = p
    shape, data, function = args
    #log.debug ( "parameters and arguments parsed." )
    #log.debug ( "least_circle: center = ( {}, {} ), radius = {}.".format ( center_col, center_row, radius ) )
    
    try:
        #log.debug ( "least_circle calling circle function" )
        #calculated_circle = mountain_circle ( ( center_col,
        calculated_circle = function ( ( center_col,
                                         center_row ),
                                       radius,
                                       shape )
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )

    try:
        #log.debug ( "least_circle calculating residue" )
        residue = calculated_circle - data
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )

    log.debug ( "residue = %f" % numpy.sum ( numpy.abs ( residue ) ) )
    return ( residue.flatten ( ) )

def fit_circle ( center_col, center_row, radius, data, function ):
    log = logging.getLogger ( __name__ )

    parameters = ( float ( center_col ),
                   float ( center_row ),
                   float ( radius ) )
    
    # Constraints on parameters
    #parinfo = [ ]
    #parbase = { #'deriv_debug' : True,
    #            'fixed'  : False,
    #            #'side'   : 2,
    #            'step'   : radius / 10 }
    #parinfo.append ( parbase )
    #parbase = { 'fixed'  : False,
    #            'step'   : radius / 10 }
    #parinfo.append ( parbase )
    #parbase = { 'fixed'  : False,
    #            'step'   : 1 }
    #parbase = { 'fixed'  : True }
    #parinfo.append ( parbase )
    
    #for entry in parinfo:
    #    log.debug ( "parinfo = %s" % str ( entry ) )
            
    #try:
    #    log.debug ( "fit_circle (fixed radius) input parameters = {}".format ( parameters ) )
    #    fit_parameters, fit_result = mpyfit.fit ( least_circle,
    #                                              parameters,
    #                                              args = ( data.shape, data, function ),
    #                                              parinfo = parinfo,
    #                                              xtol = 1e-5 )
    #except Exception as e:
    #    log.error ( tuna.console.output_exception ( e ) )
    #    raise ( e )

    #log.info ( "fit_parameters = {}".format ( fit_parameters ) )
    #log.debug ( "fit_circle (fixed radius) result = {}".format ( fit_result ) )

    #parameters = ( fit_parameters [ 0 ],
    #               fit_parameters [ 1 ],
    #               radius )
    
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
    
    for entry in parinfo:
        log.debug ( "parinfo = %s" % str ( entry ) )
            
    try:
        log.debug ( "fit_circle input parameters = {}".format ( parameters ) )
        fit_parameters, fit_result = mpyfit.fit ( least_circle,
                                                  parameters,
                                                  args = ( data.shape, data, function ),
                                                  parinfo = parinfo,
                                                  xtol = 1e-5 )
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )
        raise ( e )

    #log.info ( "fit_parameters = {}".format ( fit_parameters ) )
    log.debug ( "fit_circle result = {}".format ( fit_result ) )

    
    return fit_parameters, function (
        ( fit_parameters [ 0 ], fit_parameters [ 1 ] ), fit_parameters [ 2 ], data.shape )
