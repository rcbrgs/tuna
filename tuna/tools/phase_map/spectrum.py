# -*- coding: utf-8 -*-
"""
This module's scope are per-spectra operations.

Example::

    >>> import tuna
    >>> raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    >>> continuum_detector = tuna.tools.phase_map.continuum_detector ( can = raw ); continuum_detector.join ( )
    >>> continuum_detector.continuum.array [ 100 ] [ 100 ]
    3.0
"""
import logging
import math
import numpy
import threading
import time
import tuna

class continuum_detector ( threading.Thread ):
    """
    This class is responsible for detecting the continuum at each pixel, for a given input data cube.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor expects the following parameters:

    * can : :ref:`tuna_io_can_label`
        Containing data from a spectrograph.

    * continuum_to_FSR_ratio : float
        Encoding the ratio below which values are to be ignored.
    """
    def __init__ ( self, can, continuum_to_FSR_ratio = 0.25 ):
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )

        self.can = can
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio

        self.continuum = None
        
        self.start ( )

    def run ( self ):
        """
        Method required by :ref:`threading_label`, which allows parallel exection in a separate thread.
        """

        start = time.time ( )

        continuum_array = numpy.zeros ( shape = ( self.can.array.shape [ 1 ], 
                                                  self.can.array.shape [ 2 ] ) )

        self.log.debug ( "Continuum array 0% created." )
        last_percentage_logged = 0
        for row in range ( self.can.array.shape [ 1 ] ):
            percentage = 10 * int ( row / self.can.array.shape [ 1 ] * 10 )
            if ( percentage > last_percentage_logged ):
                last_percentage_logged = percentage
                self.log.debug ( "Continuum array %d%% created." % ( percentage ) )
            for col in range ( self.can.array.shape [ 2 ] ):
                continuum_array [ row ] [ col ] = median_of_lowest_channels ( spectrum = self.can.array [ :, row, col ], 
                                                                              continuum_to_FSR_ratio = self.continuum_to_FSR_ratio )
        
        self.log.info ( "Continuum array created." )

        self.continuum = tuna.io.can ( array = continuum_array )

        self.log.debug ( "detect_continuum() took %ds." % ( time.time ( ) - start ) )

def median_of_lowest_channels ( continuum_to_FSR_ratio = 0.25,
                                spectrum = numpy.ndarray ):
    """
    This function's goal is to obtain the median of the three lowest channels of the input profile.

    Parameters:

    * continuum_to_FSR_ratio : float : 0.25
        The ratio of signal that is expected to be part of the continuum.

    * spectrum : numpy.ndarray
        The spectral data.
    """
    log = logging.getLogger ( __name__ )

    channels = max ( 1, int ( continuum_to_FSR_ratio * spectrum.shape [ 0 ] ) )

    lowest = [ ]
    auxiliary = spectrum
    for channel in range ( channels ):
        min_index = numpy.argmin ( auxiliary )
        lowest.append ( auxiliary [ min_index ] )
        auxiliary = numpy.delete ( auxiliary, min_index )
    lowest.sort ( )

    if ( channels % 2 == 0 ):
        return ( lowest [ math.floor ( channels / 2 ) ] + lowest [ math.ceil ( channels / 2 ) ] ) / 2
    else:
        return lowest [ math.floor ( channels / 2 ) ]

def suppress_channel ( replacement,
                       array = numpy.ndarray,
                       channels = list ):
    """
    This function creates a copy of the input array, substituting the input channels list with the channels from the input replacement.

    Parameters:

    * replacement: numpy.ndarray
        Contains the signal where channels are going to be replaced from.

    * array : numpy.ndarray
        The data that is going to be copied, and the original data is from.

    * channels : list
        Lists the indexes of the channels to be substituted.
    """
    result = numpy.copy ( array )
    for channel in channels:
        result [ channel ] = numpy.copy ( replacement.array [ channel ] )
    return result
