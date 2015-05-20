import logging
from math import floor
import numpy
import threading
import time
import tuna

def average_of_lowest_channels ( array = numpy.ndarray, number_of_channels = 3 ):
    """
    Returns the average of the three lowest channels of the input profile.
    """
    auxiliary = numpy.copy ( array )
    minimum_sum = 0
    number_of_channels = min ( [ number_of_channels, array.shape [ 0 ] ] )

    for element in range ( number_of_channels ):
        minimum_index = numpy.argmin ( auxiliary )
        minimum_sum += array[minimum_index]
        next_auxiliary = [ ]
        for element in range ( auxiliary.shape[0] ):
            if element != minimum_index:
                next_auxiliary.append ( auxiliary[element] )
        auxiliary = numpy.array ( next_auxiliary )

    return minimum_sum / number_of_channels

class continuum_detector ( threading.Thread ):
    def __init__ ( self, can, continuum_to_FSR_ratio = 0.25 ):
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )

        self.can = can
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio

        self.continuum = None
        
        self.start ( )

    def run ( self ):
        start = time.time ( )

        continuum_array = numpy.zeros ( shape = ( self.can.array.shape [ 1 ], 
                                                  self.can.array.shape [ 2 ] ) )

        self.log.info ( "Continuum array 0% created." )
        last_percentage_logged = 0
        for row in range ( self.can.array.shape [ 1 ] ):
            percentage = 10 * int ( row / self.can.array.shape [ 1 ] * 10 )
            if ( percentage > last_percentage_logged ):
                last_percentage_logged = percentage
                self.log.info ( "Continuum array %d%% created." % ( percentage ) )
            for col in range ( self.can.array.shape [ 2 ] ):
                continuum_array [ row ] [ col ] = median_of_lowest_channels ( spectrum = self.can.array [ :, row, col ], 
                                                                              continuum_to_FSR_ratio = self.continuum_to_FSR_ratio )
        
        self.log.info ( "Continuum array 100% created." )

        self.continuum = tuna.io.can ( array = continuum_array )

        self.log.info ( "detect_continuum() took %ds." % ( time.time ( ) - start ) )

def median_of_lowest_channels ( continuum_to_FSR_ratio = 0.25,
                                spectrum = numpy.ndarray ):
    """
    Returns the median of the three lowest channels of the input profile.
    """
    channels = int ( continuum_to_FSR_ratio * spectrum.shape [ 0 ] )

    lowest = [ ]
    auxiliary = spectrum
    for channel in range ( channels ):
        min_index = numpy.argmin ( auxiliary )
        lowest.append ( auxiliary [ min_index ] )
        auxiliary = numpy.delete ( auxiliary, min_index )
    lowest.sort ( )

    if ( channels % 2 == 0 ):
        return ( lowest [ int ( channels / 2 ) ] + lowest [ int ( channels / 2 ) - 1 ] ) / 2
    else:
        return lowest [ floor ( channels / 2 ) ]

def suppress_channel ( replacement,
                       array = numpy.ndarray,
                       channels = list ):
    result = numpy.copy ( array )
    for channel in channels:
        result [ channel ] = numpy.copy ( replacement.array [ channel ] )
    return result
