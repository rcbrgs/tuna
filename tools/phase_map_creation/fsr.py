"""
Module fsr is responsible for computing the relative number of FSRs from the axis until each pixel.
"""

from math import sqrt
import numpy
from time import time
from tools.get_pixel_neighbours import get_pixel_neighbours

class fsr ( object ):
    """
    Responsible for computing and storing a 2D array of integers with the number of FSRs from the axis until each pixel.
    """
    def __init__ ( self, fa_distances = numpy.ndarray, iit_center = ( int, int ), log = print, fa_wrapped = numpy.ndarray ):
        super ( fsr, self ).__init__ ( )
        self.__fa_distances = fa_distances
        self.__iit_center = iit_center
        self.log = log
        self.__max_rows = fa_distances.shape [ 0 ]
        self.__max_cols = fa_distances.shape [ 1 ]
        self.__fa_wrapped = fa_wrapped

    def create_fsr_map ( self, f_ring_thickness_threshold = 3.0 ):
        """
        FSR distance array creation method.
        """
        # find how many rings are there
        fl_rings = [ ]
        for i_row in range ( self.__max_rows ):
            for i_col in range ( self.__max_cols ):
                if self.__fa_distances [ i_row ] [ i_col ] > 0:
                    b_possible_new_ring = True
                    for f_ring in fl_rings:
                        if ( ( self.__fa_distances [ i_row ] [ i_col ] < f_ring + f_ring_thickness_threshold ) and
                             ( self.__fa_distances [ i_row ] [ i_col ] > f_ring - f_ring_thickness_threshold ) ):
                            b_possible_new_ring = False
                    if b_possible_new_ring:
                        fl_rings.append ( self.__fa_distances [ i_row ] [ i_col ] )
        #self.log ( "fl_rings = %s" % str ( fl_rings ) )

        # order rings by distance
        fl_ordered_rings = sorted ( fl_rings )
        #self.log ( "fl_ordered_rings = %s" % str ( fl_ordered_rings ) )

        # attribute FSR by verifying ring-relative "position"
        i_median_channel = int ( numpy.amax ( self.__fa_wrapped ) / 2 )
        ia_fsr = numpy.ndarray ( shape = self.__fa_distances.shape, dtype = numpy.int8 )
        for i_row in range ( self.__max_rows ):
            for i_col in range ( self.__max_cols ):
                i_fsr_result = len ( fl_ordered_rings )
                f_distance = sqrt ( ( self.__iit_center [ 0 ] - i_row ) ** 2 +
                                    ( self.__iit_center [ 1 ] - i_col ) ** 2 )
                for i_fsr in range ( len ( fl_ordered_rings ) ):
                    if ( f_distance <= fl_ordered_rings [ i_fsr ] + f_ring_thickness_threshold ):
                        i_fsr_result = i_fsr
                        if ( f_distance >= fl_ordered_rings [ i_fsr ] - f_ring_thickness_threshold ):
                            if self.__fa_wrapped [ i_row ] [ i_col ] < i_median_channel:
                                i_fsr_result = i_fsr + 1
                        break
                ia_fsr [ i_row ] [ i_col ] = i_fsr_result

        return ia_fsr
        
def create_fsr_map ( fa_distances = numpy.ndarray, iit_center = ( int, int ), log = print, fa_wrapped = numpy.ndarray ):
    log ( "create_fsr_map", end='' )
    start = time ( )
    
    fsr_object = fsr ( fa_distances = fa_distances, iit_center = iit_center, log = log, fa_wrapped = fa_wrapped )
    return fsr_object.create_fsr_map ( )
    
    log ( " %ds." % ( time ( ) - start ) )
