"""
The scope of this module is to find rings within 3D FP spectrographs.
"""

import IPython
import logging
import math
import numpy
import tuna

class rings_finder ( object ):
    """
    The responsibility of this class is to find all rings contained in a data cube.
    """
    def __init__ ( self, array ):
        self.log = logging.getLogger ( __name__ )
        self.__version__ = '0.1.0'
        self.changelog = {
            '0.1.0' : "Initial version." }
        self.plot_log = True
        if self.plot_log:
            self.ipython = IPython.get_ipython()
            self.ipython.magic("matplotlib qt")

        self.chosen_plane = 1
        self.ridge_threshold = 1
        self.upper_percentile = 90

            
        self.array = array
        
        self.result = { }
        
    def execute ( self ):
        """
        1. segment the image in ring and non-ring regions.
        2. Create a separate array for each individual ring.
        3. Calculate the center and the average radius.
        """
        self.segment ( )
        self.find_continuous_regions ( )       
        self.log.debug ( "rings_finder finished." )
        
    def segment ( self ):
        if len ( self.array.shape ) != 3:
            self.log.info ( "This procedure expects a 3D numpy ndarray as input." )
        
        gradients = numpy.gradient ( self.array )
        if self.plot_log:
            tuna.tools.plot ( gradients [ 0 ] [ self.chosen_plane ], "gradients [ 0 ] [ {} ]".format (
                self.chosen_plane ), self.ipython )
            #tuna.tools.plot ( gradients [ 1 ], "Col gradients", self.ipython )
            #tuna.tools.plot ( gradients [ 2 ], "Row gradients", self.ipython )
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

    def find_continuous_regions ( self ):
        ridge = self.result [ 'ridge' ]
        painted = numpy.copy ( ridge )
        color = 1
        for col in range ( ridge.shape [ 0 ] ):
            self.log.debug ( "painted creation: col {}.".format ( col ) )
            for row in range ( ridge.shape [ 1 ] ):
                if painted [ col ] [ row ] != 0:
                    continue
                color += 1
                to_paint = [ ( col, row ) ]
                while ( len ( to_paint ) > 0 ):
                    here = to_paint.pop ( )
                    painted [ here [ 0 ] ] [ here [ 1 ] ] = color
                    neighbours = tuna.tools.get_pixel_neighbours ( here, ridge )
                    for neighbour in neighbours:
                        if painted [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] != 0:
                            continue
                        to_paint.append ( neighbour )
        if self.plot_log:
            tuna.tools.plot ( painted, "painted", self.ipython )
        self.result [ 'painted' ] = painted
        return
        color = 0
        continuous = painted - ridge
        for col in range ( continuous.shape [ 0 ] ):
            self.log.debug ( "continuous creation: col {}.".format ( col ) )
            for row in range ( continuous.shape [ 1 ] ):
                if continuous [ col ] [ row ] != 0:
                    color = continuous [ col ] [ row ]
                    continue
                to_paint = [ ( col, row ) ]
                while ( len ( to_paint ) > 0 ):
                    here = to_paint.pop ( )
                    painted [ here [ 0 ] ] [ here [ 1 ] ] = color
                    neighbours = tuna.tools.get_pixel_neighbours ( here, continuous )
                    for neighbour in neighbours:
                        if continuous [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] != 0:
                            continue
                        to_paint.append ( neighbour )
        if self.plot_log:
            tuna.tools.plot ( continuous, "continuous", self.ipython )
        self.result [ 'continuous' ] = continuous
    
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
