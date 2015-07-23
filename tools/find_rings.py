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
        self.log.setLevel ( logging.INFO )
        self.__version__ = '0.1.0'
        self.changelog = {
            '0.1.0' : "Initial version." }
        self.plot_log = True
        if self.plot_log:
            self.ipython = IPython.get_ipython()
            self.ipython.magic("matplotlib qt")

        self.upper_percentile = 99
        self.percentile_interval = 4
            
        self.array = array
        
        self.result = [ ]
        
    def execute ( self ):
        """
        1. segment the image in ring and non-ring regions.
        2. Create a separate array for each individual ring.
        3. Calculate the center and the average radius.
        """

        if len ( self.array.shape ) != 3:
            self.log.info ( "This procedure expects a 3D numpy ndarray as input." )
        
        gradients = numpy.gradient ( self.array )
        if self.plot_log:
            tuna.tools.plot ( gradients [ 0 ], "Dep gradients", self.ipython )
            #tuna.tools.plot ( gradients [ 1 ], "Col gradients", self.ipython )
            #tuna.tools.plot ( gradients [ 2 ], "Row gradients", self.ipython )

        upper_percentile_value = numpy.percentile ( gradients [ 0 ], self.upper_percentile ) 
        upper_dep_gradient = numpy.where ( gradients [ 0 ] > upper_percentile_value, 1, 0 )
        #upper_percentile_value = numpy.percentile ( gradients [ 1 ], 99 )
        #upper_col_gradient = numpy.where ( gradients [ 1 ] > upper_percentile_value,
        #                                   numpy.ones  ( shape = self.array.shape ),
        #                                   numpy.zeros ( shape = self.array.shape ) )
        #upper_percentile_value = numpy.percentile ( gradients [ 2 ], 99 )
        #upper_row_gradient = numpy.where ( gradients [ 2 ] > upper_percentile_value,
        #                                   numpy.ones  ( shape = self.array.shape ),
        #                                   numpy.zeros ( shape = self.array.shape ) )
        #if self.plot_log:
        #    tuna.tools.plot ( upper_dep_gradient, "99 percentile dep gradients", self.ipython )
        #    tuna.tools.plot ( upper_col_gradient, "99 percentile col gradients", self.ipython )
        #    tuna.tools.plot ( upper_row_gradient, "99 percentile row gradients", self.ipython )
        #
        #col_or_row = numpy.logical_or ( upper_col_gradient, upper_row_gradient )
        #col_or_row_numerical = numpy.where ( col_or_row == True,
        #                                     1, 0 )
        #dep_and_col_or_row = numpy.where ( numpy.logical_and ( upper_dep_gradient, col_or_row ),
        #                                   1, 0 )
        #if self.plot_log:
        #    tuna.tools.plot ( col_or_row_numerical, "col or row", self.ipython )
        #    tuna.tools.plot ( dep_and_col_or_row, "dep AND ( col or row )", self.ipython )

        lower_percentile = self.upper_percentile - self.percentile_interval
        lower_percentile_value = numpy.percentile ( gradients [ 0 ], lower_percentile ) 
        lower_dep_gradient = numpy.where ( gradients [ 0 ] > lower_percentile_value, 1, 0 )

        #diff_dep_gradient = numpy.where ( upper_dep_gradient - lower_dep_gradient > 0, 1, 0 )
        diff_dep_gradient = lower_dep_gradient - upper_dep_gradient 
        if self.plot_log:
            tuna.tools.plot ( upper_dep_gradient, "{} percentile dep gradients".format (
                self.upper_percentile ), self.ipython )
            tuna.tools.plot ( lower_dep_gradient, "{} percentile dep gradients".format (
                lower_percentile ), self.ipython )
            tuna.tools.plot ( diff_dep_gradient, "Diff percentile dep gradients", self.ipython )

        self.log.debug ( "rings_finder finished." )

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
