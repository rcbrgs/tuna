"""
Module fsr is responsible for computing the relative number of FSRs from the axis until each pixel.
"""

import logging
from math import sqrt
import numpy
import threading
import time
import tuna

class fsr_mapper ( threading.Thread ):
    """
    Responsible for computing and storing a 2D array of integers with the number of FSRs from the axis until each pixel.
    """
    def __init__ ( self, distances, wrapped, center ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        super ( self.__class__, self ).__init__ ( )

        self.distances = distances.array
        self.center = center
        self.wrapped = wrapped.array

        self.max_rows = distances.shape [ 0 ]
        self.max_cols = distances.shape [ 1 ]

        self.fsr = None

        self.start ( )

    def run ( self ):
        start = time.time ( )

        self.create_fsr_map ( )

        self.log.info ( "create_fsr_map() took %ds." % ( time.time ( ) - start ) )

    def create_fsr_map ( self ):
        """
        FSR distance array creation method.
        """
        ring_thickness_threshold = self.estimate_ring_thickness ( )
        self.log.debug ( "ring_thickness_threshold = %f" % ring_thickness_threshold )
        # find how many rings are there
        rings = [ ]
        self.log.debug ( "fsr array 0% created." )
        last_percentage_logged = 0
        for row in range ( self.max_rows ):
            percentage = 10 * int ( row / self.max_rows * 10 )
            if percentage > last_percentage_logged:
                last_percentage_logged = percentage
                self.log.debug ( "fsr array %d%% created." % percentage )
            for col in range ( self.max_cols ):
                if self.distances [ row ] [ col ] > 0:
                    possible_new_ring = True
                    for ring in rings:
                        if ( ( self.distances [ row ] [ col ] < ring + ring_thickness_threshold ) and
                             ( self.distances [ row ] [ col ] > ring - ring_thickness_threshold ) ):
                            possible_new_ring = False
                    if possible_new_ring:
                        rings.append ( self.distances [ row ] [ col ] )
        self.log.info ( "fsr array created." )
        #self.log ( "fl_rings = %s" % str ( rings ) )

        # order rings by distance
        ordered_rings = sorted ( rings )
        #self.log ( "fl_ordered_rings = %s" % str ( ordered_rings ) )

        # attribute FSR by verifying ring-relative "position"
        median_channel = int ( numpy.amax ( self.wrapped ) / 2 )
        fsr = numpy.ndarray ( shape = self.distances.shape, dtype = numpy.int8 )
        for row in range ( self.max_rows ):
            for col in range ( self.max_cols ):
                fsr_result = len ( ordered_rings )
                distance = sqrt ( ( self.center [ 0 ] - row ) ** 2 +
                                  ( self.center [ 1 ] - col ) ** 2 )
                for fsr_range in range ( len ( ordered_rings ) ):
                    if ( distance <= ordered_rings [ fsr_range ] + ring_thickness_threshold ):
                        fsr_result = fsr_range
                        if ( distance >= ordered_rings [ fsr_range ] - ring_thickness_threshold ):
                            if self.wrapped [ row ] [ col ] < median_channel:
                                fsr_result = fsr_range + 1
                        break
                fsr [ row ] [ col ] = fsr_result

        self.fsr = fsr

    def estimate_ring_thickness ( self ):
        distances = numpy.unique ( self.distances.astype ( numpy.int16 ) )
        self.log.debug ( "distances = %s" % str ( distances ) )

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
        self.log.debug ( "ranges = %s" % str ( ranges ) )

        if ranges == [ [ ] ]:
            return 0

        thicknesses = [ ranges [ 0 ] [ 0 ] ]
        for thickness in range ( 1, len ( ranges ) ):
            thicknesses.append ( ranges [ thickness ] [ 0 ] - ranges [ thickness - 1 ] [ -1 ] )
        self.log.debug ( "thicknesses = %s" % str ( thicknesses ) )

        return int ( max ( min ( thicknesses ) * 0.25, 20 ) )
        
    def estimate_ring_thickness_old ( self ):
        distances = numpy.unique ( self.distances.astype ( numpy.int16 ) )
        self.log.debug ( "distances = %s" % str ( distances ) )

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
        self.log.debug ( "ranges = %s" % str ( ranges ) )
        thicknesses = [ ]
        for range in ranges:
            thicknesses.append ( len ( range ) )
        self.log.debug ( "thicknesses = %s" % str ( thicknesses ) )
        return max ( thicknesses )
        
