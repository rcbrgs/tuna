# -*- coding: utf-8 -*-
"""
This module's scope is the detection and mapping of borders in a wrapped phase map.

Example::

    >>> import tuna
    >>> raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    >>> barycenter = tuna.plugins.run ( "Barycenter algorithm" ) ( data_can = raw )
    >>> noise = tuna.plugins.run ( "Noise detector" ) ( data = raw, \
                                                        wrapped = barycenter, \
                                                        noise_mask_radius = 1, \
                                                        noise_threshold = 1 )
    >>> rings = tuna.plugins.run ( "Ring center finder" ) ( data = raw.array, \
                                                            min_rings = 2 )
    >>> borders = tuna.tools.phase_map.ring_border_detector ( barycenter, ( 219, 255 ), noise, rings ); borders.join ( )
    >>> borders.distances.array [ 0 ] [ 170 : 190 ]
    array([   0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ,
            231.82699114,  231.82699114,  231.82699114,    0.        ,
              0.        ,    0.        ,    0.        ,    0.        ])
"""

import logging
from math import sqrt
import numpy
import threading
import time
import tuna

class ring_border_detector ( threading.Thread ):
    """
    This class is responsible for detecting the "borders" of the rings contained in a interferogram. 

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor has the following signature:

    Parameters:

    * data : numpy.ndarray
        Containing the wrapped phase map.

    * center : tuple of 2 integers
        Which correspond to the pixel center of the interferograph.

    * noise : :ref:`tuna_io_can_label`
        Containing the noise map for data.

    * rings : dictionary
        Such as the one produced by  :ref:`tuna_tools_spectral_rings_fitter_label` or equivalent.

    * log_level : valid :ref:`logging_label` level : logging.INFO
        Will set the log output to the specified level.
    """
    def __init__ ( self, data, center, noise, rings, log_level = logging.INFO ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( log_level )
        super ( self.__class__, self ).__init__ ( )

        self.data = data
        self.center = center
        self.noise = noise.array
        self.rings = rings

        self.borders = None
        self.discontinuities = None
        self.discontinuities_distances = None
        self.distances = None

        self.start ( )

    def run ( self ):
        """
        Method required by :ref:`threading_label`, which allows parallel exection in a separate thread.
        
        First, this tool will aggregate all circles contained in the input rings dictionary. Then, it will map the distances from each pixel in the borders to the center of the rings structure. This is saved as the distances numpy.ndarray.
        """
        start = time.time ( )

        self.log.debug ( "self.center = {}".format ( self.center ) )
        self.generate_borders_map_from_wrapped ( )
        self.map_distances_onto_borders ( )
        self.distances = tuna.io.can ( self.borders )

        self.log.debug ( "ring_border_detector took %ds." % ( time.time ( ) - start ) )
                
    def generate_borders_map_from_wrapped ( self ):
        """
        The directional gradients from the wrapped phase map will have low values everywhere, except at the transition from 0 to max channel, indicative of an order change.
        This method will detect that and mark the border pixels with a one, and zero everywhere else.
        """
        gradient = numpy.gradient ( self.data.array )
        wrapped_gradient = gradient [ 0 ]
        average = numpy.average ( wrapped_gradient )
        zeroes = numpy.zeros ( shape = self.data.shape )
        ones = numpy.ones ( shape = self.data.shape )
        half = numpy.where ( wrapped_gradient > average - 1, zeroes, ones )
        other_half = numpy.where ( wrapped_gradient < average + 1, zeroes, ones )
        complete = half + other_half
        self.borders = numpy.zeros ( shape = self.data.array.shape )
        for col in range ( self.data.array.shape [ 0 ] ):
            for row in range ( self.data.array.shape [ 1 ] ):
                if self.noise [ col ] [ row ] == 1:
                    continue
                self.borders [ col ] [ row ]  = complete [ col ] [ row ]
        
    def map_distances_onto_borders ( self ):
        """
        This method will map the pixels belonging to the border with the value of the radius of its nearest ring. Essentially, the objective is to have every pixel that belongs to a certain "border" to have the same non-zero value, and for different ring borders to have different values.
        """
        for col in range ( self.borders.shape [ 0 ] ):
            for row in range ( self.borders.shape [ 1 ] ):
                if self.borders [ col ] [ row ] == 0:
                    continue
                distance = tuna.tools.calculate_distance ( self.center, ( col, row ) )
                self.borders [ col ] [ row ] = distance
