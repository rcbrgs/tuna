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
        self.__version__ = '0.1.5'
        self.changelog = {
            '0.1.5' : "Use sympy to find median line, instead of relying on less precise pixelated logic.",
            '0.1.4' : "Clean up unnecessary code. Restrict algorithm only to sets with more than 10 pixels.",
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
        count = 0
        for pixel_set in self.result [ 'ring_pixel_sets' ]:
            self.log.debug ( "attempting to fit set {}".format ( count ) )

            minimal_point, minimal_radius = self.construct_ring_center ( pixel_set )
                
            ring_parameters, ring_fit = fit_circle ( minimal_point [ 0 ],
                                                     minimal_point [ 1 ],
                                                     minimal_radius,
                                                     pixel_set,
                                                     circle )
            
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

    def construct_ring_center ( self, pixel_set ):
        """
        Returns estimats for the center and radius of a circle that is osculatory to the curve contained in the pixel_set.
        
        Arguments:
        - pixel_set is a 2D numpy array where each pixel has either a 0 or a 1 as value.

        Returns:

        center, radius where center is a 2-tuple of floats and radius is a float.
        """
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
        sympy_mid_point = sympy.Point ( mid_point [ 0 ], mid_point [ 1 ] )
        construction [ mid_point [ 0 ] ] [ mid_point [ 1 ] ] = color
        self.log.debug ( "mid_point = {}".format ( mid_point ) )

        #min_distance = math.sqrt ( pixel_set.shape [ 0 ] ** 2 + pixel_set.shape [ 1 ] ** 2 )
        #for pixel in pixels:
        #    distance = tuna.tools.calculate_distance ( pixel, mid_point )
        #    if distance <= min_distance:
        #        min_distance = distance
        #        min_pixel = pixel
        #construction [ min_pixel [ 0 ] ] [ min_pixel [ 1 ] ] = color
        
        #self.log.debug ( "min_distance = {}".format ( min_distance ) )
        #self.log.debug ( "min_pixel = {}".format ( min_pixel ) )
        #ratio = min_distance / max_distance
        #self.log.debug ( "ratio = {}".format ( ratio ) )

        chord_extreme_1 = sympy.Point ( max_pair [ 0 ] [ 0 ], max_pair [ 0 ] [ 1 ] )
        chord_extreme_2 = sympy.Point ( max_pair [ 1 ] [ 0 ], max_pair [ 1 ] [ 1 ] )
        chord_line = sympy.Line ( chord_extreme_1, chord_extreme_2 )
        self.plot_sympy_line ( construction, chord_line, color )

        #concurrent_extreme_min = sympy.Point ( min_pixel [ 0 ], min_pixel [ 1 ] )
        #concurrent_extreme_mid = sympy.Point ( mid_point [ 0 ], mid_point [ 1 ] )
        concurrent_line = chord_line.perpendicular_line ( sympy_mid_point )
        self.plot_sympy_line ( construction, concurrent_line, color )

        min_distance = math.sqrt ( pixel_set.shape [ 0 ] ** 2 + pixel_set.shape [ 1 ] ** 2 )
        for pixel in pixels:
            sympy_point = sympy.Point ( pixel [ 0 ], pixel [ 1 ] )
            projection = concurrent_line.projection ( sympy_point )
            distance = tuna.tools.calculate_distance ( pixel, ( projection.x, projection.y ) )
            if distance <= min_distance:
                min_distance = distance
                min_pixel = pixel
                concurrent_extreme_min = projection
        construction [ min_pixel [ 0 ] ] [ min_pixel [ 1 ] ] = color
        
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

        for neighbour in tuna.tools.get_pixel_neighbours (
                ( round ( center [ 0 ] ), round ( center [ 1 ] ) ), construction ):
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

        for pixels_set in connected_pixels_sets:
            if len ( pixels_set ) < 10:
                continue
            set_array = numpy.zeros ( shape = array.shape )
            for pixel in pixels_set:
                set_array [ pixel [ 0 ] ] [ pixel [ 1 ] ] = 1
            try:
                self.result [ 'ring_pixel_sets' ].append ( set_array )
            except KeyError:
                self.result [ 'ring_pixel_sets' ] = [ set_array ]

        self.log.debug ( "{} pixels_sets found.".format ( len ( self.result [ 'ring_pixel_sets' ] ) ) )
        if self.plot_log:
            count = 0
            for pixel_set in self.result [ 'ring_pixel_sets' ]:
                tuna.tools.plot ( pixel_set, "pixel_set {}".format ( count ), self.ipython )
                count += 1
            
def find_rings ( array, plane ):
    """
    Attempts to find rings contained in a 3D numpy ndarray input.
    Parameters:
    - array is the 3D numpy array with the spectrograph.
    - plane is the index in the cube for the spectrograph whose rings the user wants.

    Returns a list of dicts, with the following keys:
    'array'  : 2D numpy.ndarray where pixels in the ring have value 1 and other pixels have value 0.
    'center' : a tuple of 2 floats, where the first is the column and the second is the row of the most probable locations for the center of that ring.
    'radius' : a float with the average value of the distance of the ring pixels to its center.
    'construction' : a list of numpy arrays containing the geometric construction that led to the estimated center and radius used in the fit.
    'pixel_set' : a list of numpy arrays containing the segmented pixel sets corresponding to each identified ring.
    """

    finder = rings_finder ( array, plane )
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

    return distances

def least_circle ( p, args ):
    log = logging.getLogger ( __name__ )
    center_col, center_row, radius = p
    shape, data, function = args
    
    try:
        calculated_circle = function ( ( center_col,
                                         center_row ),
                                       radius,
                                       shape )
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) )

    try:
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

    log.debug ( "fit_circle result = {}".format ( fit_result ) )

    
    return fit_parameters, function (
        ( fit_parameters [ 0 ], fit_parameters [ 1 ] ), fit_parameters [ 2 ], data.shape )
