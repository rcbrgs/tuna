from math import floor
import numpy
from time import time

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

def create_continuum_array ( array = numpy.ndarray,
                             f_continuum_to_FSR_ratio = float,
                             log = print ):
    """
    Returns a 2D numpy ndarray where each pixel has the value of the continuum level of the input 3D array.
    """
    i_start = time ( )
    

    continuum_array = numpy.ndarray ( shape = ( array.shape[1], array.shape[2] ) )
    for row in range ( array.shape[1] ):
        for col in range ( array.shape[2] ):
            #continuum_array[row][col] = average_of_lowest_channels ( array = array[:,row,col], 
            continuum_array[row][col] = median_of_lowest_channels ( a_spectrum = array [ :, row, col ], 
                                                                    f_continuum_to_FSR_ratio = f_continuum_to_FSR_ratio )

    log ( "info: create_continuum_array() took %ds." % ( time ( ) - i_start ) )
    return continuum_array

def median_of_lowest_channels ( f_continuum_to_FSR_ratio = 0.5,
                                a_spectrum = numpy.ndarray ):
    """
    Returns the median of the three lowest channels of the input profile.
    """
    a_auxiliary = numpy.copy ( a_spectrum )
    i_channels = int ( f_continuum_to_FSR_ratio * a_spectrum.shape [ 0 ] )
    l_lowest = [ ]
    for i_channel in range ( i_channels ):
        l_lowest.append ( numpy.amin ( a_auxiliary ) )
        a_auxiliary = numpy.delete ( a_auxiliary, numpy.argmin ( a_auxiliary ) )
    l_lowest.sort ( )

    if ( i_channels % 2 == 0 ):
        return ( l_lowest [ i_channels / 2 ] + l_lowest [ i_channels / 2 - 1 ] ) / 2
    else:
        return l_lowest [ floor ( i_channels / 2 ) ]
