# -*- coding: utf-8 -*-
"""
Module fsr is responsible for computing the relative number of FSRs from the axis until each pixel.

Example usage::

    >>> import tuna
    >>> raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    >>> barycenter = tuna.tools.phase_map.barycenter_fast ( raw ); barycenter.join ( )
    >>> noise_detector = tuna.tools.phase_map.noise_detector ( raw, barycenter.result, 1, 1 ); noise_detector.join ( )
    >>> rings = tuna.tools.find_rings ( raw.array, min_rings = 2 )
    >>> borders = tuna.tools.phase_map.ring_border_detector ( barycenter.result, ( 219, 255 ), noise_detector.noise, rings ); borders.join ( )
    >>> fsr = tuna.tools.phase_map.fsr_mapper ( distances = borders.distances, wrapped = barycenter.result, center = ( 219, 255 ), concentric_rings = rings [ 'concentric_rings' ] ); fsr.join ( )
    >>> fsr.distances [ 0 ] [ 150 : 200 ]
    array([   0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,  231.82699114,  231.82699114,  231.82699114,
            231.82699114,  231.82699114,  231.82699114,  231.82699114,
            231.82699114,  231.82699114,  231.82699114,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ])
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

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor has the following signature:

    Parameters:

    * distances : can
        Containing the map of border distances to the center.

    * wrapped : can
        Containing the wrapped phase map.

    * center : tuple of 2 integers
        Containing the column and row of the center.

    * concentric_rings : dictionary
        A structure describing the geometry of the concentric rings characteristic of a Fabry-Pérot interferogram.
    """
    def __init__ ( self, distances, wrapped, center, concentric_rings ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = '0.1.1'
        self.changelog = {
            "0.1.1" : "Tuna 0.14.0 : improved documentation.",
            '0.1.0' : "First changeloged version."
            }
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.distances = distances.array
        self.center = center
        self.wrapped = wrapped.array
        self.concentric_rings = concentric_rings

        self.max_rows = distances.shape [ 0 ]
        self.max_cols = distances.shape [ 1 ]

        self.fsr = None

        self.start ( )

    def run ( self ):
        """
        Thread run method.
        """
        start = time.time ( )

        #self.create_fsr_map ( )
        self.create_fsr_map_from_rings ( )

        self.log.debug ( "create_fsr_map() took %ds." % ( time.time ( ) - start ) )

    def create_fsr_map_from_rings ( self ):
        """
        Using the ring map and the wrapped phase map, this method will create a numpy.ndarray with the same dimensions as these inputs, where each pixel will have an integer value corresponding to how many times the spectrum has been "wrapped" at that pixel. 
        """
        thickness = 10
        half_channels = numpy.max ( self.wrapped ) / 2
        max_order = len ( self.concentric_rings [ 1 ] )
        sorted_radii = sorted ( self.concentric_rings [ 1 ] )
        sorted_radii.append ( float ( 'inf' ) )
        self.fsr = numpy.ndarray ( shape = self.wrapped.shape )
        for col in range ( self.wrapped.shape [ 0 ] ):
            for row in range ( self.wrapped.shape [ 1 ] ):
                order = None
                distance = tuna.tools.calculate_distance ( ( col, row ), self.concentric_rings [ 0 ] )
                # treat "border pixels"
                for radius_index in range ( len ( sorted_radii ) ):
                    border_distance = abs ( distance - sorted_radii [ radius_index ] )
                    if border_distance <= thickness:
                        if self.wrapped [ col ] [ row ] > half_channels:
                            order = radius_index
                        else:
                            order = radius_index + 1
                        break
                if order != None:
                    self.fsr [ col ] [ row ] = order
                    continue

                # treat "band pixels"
                order = max_order
                for radius_index in range ( len ( sorted_radii ) ):
                    if distance < sorted_radii [ radius_index ]:
                        self.fsr [ col ] [ row ] = radius_index
                        break
                    
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

        # order rings by distance
        ordered_rings = sorted ( rings )

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
        """
        Attempts to guess the "thickness" of a ring, that is, how far apart the concentric rings are.
        """
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
