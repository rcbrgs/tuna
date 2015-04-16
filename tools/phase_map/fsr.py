"""
Module fsr is responsible for computing the relative number of FSRs from the axis until each pixel.
"""

from math import sqrt
import numpy
from time import time
from tuna.tools.get_pixel_neighbours import get_pixel_neighbours

class fsr ( object ):
    """
    Responsible for computing and storing a 2D array of integers with the number of FSRs from the axis until each pixel.
    """
    def __init__ ( self, 
                   distances = numpy.ndarray, 
                   center = ( int, int ), 
                   log = print, 
                   wrapped = numpy.ndarray ):
        super ( fsr, self ).__init__ ( )
        self.__distances = distances
        self.__center = center
        self.log = log
        self.__max_rows = distances.shape [ 0 ]
        self.__max_cols = distances.shape [ 1 ]
        self.__wrapped = wrapped

    def create_fsr_map ( self ):
        """
        FSR distance array creation method.
        """
        ring_thickness_threshold = self.estimate_ring_thickness ( )
        self.log ( "debug: ring_thickness_threshold = %f" % ring_thickness_threshold )
        # find how many rings are there
        rings = [ ]
        for row in range ( self.__max_rows ):
            for col in range ( self.__max_cols ):
                if self.__distances [ row ] [ col ] > 0:
                    possible_new_ring = True
                    for ring in rings:
                        if ( ( self.__distances [ row ] [ col ] < ring + ring_thickness_threshold ) and
                             ( self.__distances [ row ] [ col ] > ring - ring_thickness_threshold ) ):
                            possible_new_ring = False
                    if possible_new_ring:
                        rings.append ( self.__distances [ row ] [ col ] )
        #self.log ( "fl_rings = %s" % str ( rings ) )

        # order rings by distance
        ordered_rings = sorted ( rings )
        #self.log ( "fl_ordered_rings = %s" % str ( ordered_rings ) )

        # attribute FSR by verifying ring-relative "position"
        median_channel = int ( numpy.amax ( self.__wrapped ) / 2 )
        fsr = numpy.ndarray ( shape = self.__distances.shape, dtype = numpy.int8 )
        for row in range ( self.__max_rows ):
            for col in range ( self.__max_cols ):
                fsr_result = len ( ordered_rings )
                distance = sqrt ( ( self.__center [ 0 ] - row ) ** 2 +
                                  ( self.__center [ 1 ] - col ) ** 2 )
                for fsr_range in range ( len ( ordered_rings ) ):
                    if ( distance <= ordered_rings [ fsr_range ] + ring_thickness_threshold ):
                        fsr_result = fsr_range
                        if ( distance >= ordered_rings [ fsr_range ] - ring_thickness_threshold ):
                            if self.__wrapped [ row ] [ col ] < median_channel:
                                fsr_result = fsr_range + 1
                        break
                fsr [ row ] [ col ] = fsr_result

        return fsr

    def estimate_ring_thickness ( self ):
        distances = numpy.unique ( self.__distances.astype ( numpy.int16 ) )
        self.log ( "debug: distances = %s" % str ( distances ) )

        distances_sequences = [ ]
        ranges = [ ]
        for col in range ( distances.shape [ 0 ] ):
            this_distance = distances [ col ]
            if this_distance != 0:
                if distances_sequences == [ ]:
                    distances_sequences.append ( this_distance )
                    continue
                last_distance = distances_sequences [ -1 ]
                if ( this_distance == last_distance + 1 ):
                    distances_sequences.append ( this_distance )
                    continue
                else:
                    ranges.append ( distances_sequences )
                    distances_sequences = [ this_distance ]
        if distances_sequences not in ranges:
            ranges.append ( distances_sequences )
        self.log ( "debug: ranges = %s" % str ( ranges ) )

        if ranges == [ [ ] ]:
            return 0

        thicknesses = [ ranges [ 0 ] [ 0 ] ]
        for thickness in range ( 1, len ( ranges ) ):
            thicknesses.append ( ranges [ thickness ] [ 0 ] - ranges [ thickness - 1 ] [ -1 ] )
        self.log ( "debug: thicknesses = %s" % str ( thicknesses ) )

        return int ( max ( min ( thicknesses ) * 0.25, 20 ) )
        
    def estimate_ring_thickness_old ( self ):
        distances = numpy.unique ( self.__distances.astype ( numpy.int16 ) )
        self.log ( "debug: distances = %s" % str ( distances ) )

        distances_sequences = [ ]
        ranges = [ ]
        for col in range ( distances.shape [ 0 ] ):
            this_distance = distances [ col ]
            if this_distance != 0:
                if distances_sequences == [ ]:
                    distances_sequences.append ( this_distance )
                    continue
                last_distance = distances_sequences [ -1 ]
                if ( this_distance == last_distance + 1 ):
                    distances_sequences.append ( this_distance )
                    continue
                else:
                    ranges.append ( distances_sequences )
                    distances_sequences = [ this_distance ]
        if distances_sequences not in ranges:
            ranges.append ( distances_sequences )
        self.log ( "debug: ranges = %s" % str ( ranges ) )
        thicknesses = [ ]
        for range in ranges:
            thicknesses.append ( len ( range ) )
        self.log ( "debug: thicknesses = %s" % str ( thicknesses ) )
        return max ( thicknesses )
        
def create_fsr_map ( distances = numpy.ndarray, 
                     center = ( int, int ), 
                     log = print, 
                     wrapped = numpy.ndarray ):
    start = time ( )
    
    fsr_object = fsr ( distances = distances, 
                       center = center, 
                       log = log, 
                       wrapped = wrapped )

    log ( "info: create_fsr_map() took %ds." % ( time ( ) - start ) )
    return fsr_object.create_fsr_map ( )
