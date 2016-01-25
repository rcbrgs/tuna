# -*- coding: utf-8 -*-
"""
Module fsr is responsible for computing the relative number of FSRs from the axis until each pixel.

Example usage::

    >>> import tuna
    >>> raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    >>> barycenter = tuna.plugins.run ( "Barycenter algorithm" ) ( raw )
    >>> noise = tuna.plugins.run ( "Noise detector" ) ( data = raw, \
                                                        wrapped = barycenter, \
                                                        noise_threshold = 1, \
                                                        noise_mask_radius = 1 )
    >>> rings = tuna.plugins.run ( "Ring center finder" ) ( data = raw.array, min_rings = 2 )
    >>> borders = tuna.tools.phase_map.ring_border_detector ( barycenter, ( 219, 255 ), noise, rings ); borders.join ( )
    >>> fsr = tuna.plugins.run ( "FSR mapper" ) ( distances = borders.distances, wrapped = barycenter, center = ( 219, 255 ), concentric_rings = rings [ 'concentric_rings' ] )
    >>> fsr.array [ 0 ] [ 150 : 200 ]
    array([ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
            1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
            1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
            1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.])
"""

import logging
from math import sqrt
import numpy
import threading
import time
import tuna

class fsr ( threading.Thread ):
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

        self.create_fsr_from_radii ( )

        self.log.debug ( "create_fsr_map() took %ds." % ( time.time ( ) - start ) )

    def create_fsr_from_radii ( self ):
        """
        Supposing the borders map and the concentric rings center are available, this method will generate a list of typical distances from border to center, and create a order map using this list. 
        """
        center = self.concentric_rings [ 0 ]
        self.log.debug ( "self.distances.shape == {}".format ( self.distances.shape ) )
        cols = self.distances.shape [ 0 ]
        rows = self.distances.shape [ 1 ]
        distances_list = [ ]
        for element in numpy.unique ( self.distances ):
            distances_list.append ( element )
        distances_list.remove ( 0 )
        self.log.debug ( "distances_list == {}".format ( distances_list ) )
        target_number = len ( self.concentric_rings [ 1 ] )
        filtered_distances = [ ]
        threshold = max ( distances_list )
        while ( len ( filtered_distances ) < target_number ):
            filtered_distances = [ ]
            threshold -= 1
            for entry in distances_list:
                contained = False
                for filtered in filtered_distances:
                    if filtered - threshold < float ( entry ) < filtered + threshold:
                        contained = True
                if not contained:
                    filtered_distances.append ( float ( entry ) )
            self.log.debug ( "threshold == {}, filtered_distances == {}".format ( threshold, filtered_distances ) )
            
        sorted_distances = sorted ( filtered_distances )
        self.log.info ( "sorted_distances == {}".format ( sorted_distances ) )
        
        self.fsr = numpy.zeros ( shape = self.distances.shape )
        for col in range ( cols ):
            for row in range ( rows ):
                distance = tuna.tools.calculate_distance ( center, ( col, row ) )
                for entry in range ( len ( sorted_distances ) ):
                    if entry == 0:
                        low_limit = sorted_distances [ entry ] * 0.9
                    else:
                        low_limit = sorted_distances [ entry ] - ( sorted_distances [ entry ] - sorted_distances [ entry - 1 ] ) / 4
                    if entry == len ( sorted_distances ) - 1:
                        high_limit = sorted_distances [ entry ] * 1.1
                    else:
                        high_limit = sorted_distances [ entry ] + ( sorted_distances [ entry + 1 ] - sorted_distances [ entry ] ) / 4
                    if distance >= high_limit:
                        self.fsr [ col ] [ row ] = entry + 1
                    if low_limit < distance < high_limit:
                        if self.wrapped [ col ] [ row ] < numpy.amax ( self.wrapped ) / 2:
                            self.fsr [ col ] [ row ] = entry + 1
                            break
                        else:
                            self.fsr [ col ] [ row ] = entry
                            break

def fsr_mapper ( distances : tuna.io.can,
                 wrapped : tuna.io.can,
                 center : tuple,
                 concentric_rings : dict ) -> tuna.io.can:
    """
    This function's goal is to conveniently compute a 2D array of integers with the number of FSRs from the axis until each pixel.

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

    Returns:

    * tuna.io.can 
        Containing the order map as calculated from the input.
    """
    mapper = fsr ( distances, wrapped, center, concentric_rings )
    mapper.join ( )
    return tuna.io.can ( array = mapper.fsr )
