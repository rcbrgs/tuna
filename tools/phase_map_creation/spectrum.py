import numpy
from time import time

def create_continuum_array ( array = numpy.ndarray ):
    """
    Returns a 2D numpy ndarray where each pixel has the value of the continuum level of the input 3D array.
    """
    i_start = time ( )
    print ( "create_continuum_array", end='' )

    continuum_array = numpy.ndarray ( shape = ( array.shape[1], array.shape[2] ) )
    for row in range ( array.shape[1] ):
        for col in range ( array.shape[2] ):
            continuum_array[row][col] = average_of_lowest_channels ( array = array[:,row,col], 
                                                                     number_of_channels = 3 )

    print ( " %ds." % ( time ( ) - i_start ) )
    return continuum_array

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
