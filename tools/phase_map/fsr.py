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
    def __init__ ( self, 
                   fa_distances = numpy.ndarray, 
                   iit_center = ( int, int ), 
                   log = print, 
                   fa_wrapped = numpy.ndarray ):
        super ( fsr, self ).__init__ ( )
        self.__a_distances = fa_distances
        self.__iit_center = iit_center
        self.log = log
        self.__max_rows = fa_distances.shape [ 0 ]
        self.__max_cols = fa_distances.shape [ 1 ]
        self.__fa_wrapped = fa_wrapped

    def create_fsr_map ( self ):
        """
        FSR distance array creation method.
        """
        f_ring_thickness_threshold = self.estimate_ring_thickness ( )
        self.log ( "debug: f_ring_thickness_threshold = %f" % f_ring_thickness_threshold )
        # find how many rings are there
        fl_rings = [ ]
        for i_row in range ( self.__max_rows ):
            for i_col in range ( self.__max_cols ):
                if self.__a_distances [ i_row ] [ i_col ] > 0:
                    b_possible_new_ring = True
                    for f_ring in fl_rings:
                        if ( ( self.__a_distances [ i_row ] [ i_col ] < f_ring + f_ring_thickness_threshold ) and
                             ( self.__a_distances [ i_row ] [ i_col ] > f_ring - f_ring_thickness_threshold ) ):
                            b_possible_new_ring = False
                    if b_possible_new_ring:
                        fl_rings.append ( self.__a_distances [ i_row ] [ i_col ] )
        #self.log ( "fl_rings = %s" % str ( fl_rings ) )

        # order rings by distance
        fl_ordered_rings = sorted ( fl_rings )
        #self.log ( "fl_ordered_rings = %s" % str ( fl_ordered_rings ) )

        # attribute FSR by verifying ring-relative "position"
        i_median_channel = int ( numpy.amax ( self.__fa_wrapped ) / 2 )
        ia_fsr = numpy.ndarray ( shape = self.__a_distances.shape, dtype = numpy.int8 )
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

    def estimate_ring_thickness ( self ):
        a_distances = numpy.unique ( self.__a_distances.astype ( numpy.int16 ) )
        self.log ( "debug: a_distances = %s" % str ( a_distances ) )

        l_distances = [ ]
        l_ranges = [ ]
        for i_col in range ( a_distances.shape [ 0 ] ):
            i_this_distance = a_distances [ i_col ]
            if i_this_distance != 0:
                if l_distances == [ ]:
                    l_distances.append ( i_this_distance )
                    continue
                i_last_distance = l_distances [ -1 ]
                if ( i_this_distance == i_last_distance + 1 ):
                    l_distances.append ( i_this_distance )
                    continue
                else:
                    l_ranges.append ( l_distances )
                    l_distances = [ i_this_distance ]
        if l_distances not in l_ranges:
            l_ranges.append ( l_distances )
        self.log ( "debug: l_ranges = %s" % str ( l_ranges ) )

        if l_ranges == [ [ ] ]:
            return 0

        l_thicknesses = [ l_ranges [ 0 ] [ 0 ] ]
        for l_range in range ( 1, len ( l_ranges ) ):
            l_thicknesses.append ( l_ranges [ l_range ] [ 0 ] - l_ranges [ l_range - 1 ] [ -1 ] )
        self.log ( "debug: l_thicknesses = %s" % str ( l_thicknesses ) )

        return int ( max ( min ( l_thicknesses ) * 0.25, 10 ) )
        
    def estimate_ring_thickness_old ( self ):
        a_distances = numpy.unique ( self.__a_distances.astype ( numpy.int16 ) )
        self.log ( "debug: a_distances = %s" % str ( a_distances ) )

        l_distances = [ ]
        l_ranges = [ ]
        for i_col in range ( a_distances.shape [ 0 ] ):
            i_this_distance = a_distances [ i_col ]
            if i_this_distance != 0:
                if l_distances == [ ]:
                    l_distances.append ( i_this_distance )
                    continue
                i_last_distance = l_distances [ -1 ]
                if ( i_this_distance == i_last_distance + 1 ):
                    l_distances.append ( i_this_distance )
                    continue
                else:
                    l_ranges.append ( l_distances )
                    l_distances = [ i_this_distance ]
        if l_distances not in l_ranges:
            l_ranges.append ( l_distances )
        self.log ( "debug: l_ranges = %s" % str ( l_ranges ) )
        l_thicknesses = [ ]
        for l_range in l_ranges:
            l_thicknesses.append ( len ( l_range ) )
        self.log ( "debug: l_thicknesses = %s" % str ( l_thicknesses ) )
        return max ( l_thicknesses )
        
def create_fsr_map ( fa_distances = numpy.ndarray, 
                     iit_center = ( int, int ), 
                     log = print, 
                     fa_wrapped = numpy.ndarray ):
    start = time ( )
    
    fsr_object = fsr ( fa_distances = fa_distances, 
                       iit_center = iit_center, 
                       log = log, 
                       fa_wrapped = fa_wrapped )

    log ( "info: create_fsr_map() took %ds." % ( time ( ) - start ) )
    return fsr_object.create_fsr_map ( )
