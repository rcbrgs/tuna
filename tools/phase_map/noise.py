from math import ceil, sqrt
import numpy
#from tuna.tools.get_pixel_neighbours import get_pixel_neighbours
from time import time
import tuna

def detect_noise ( array = None, 
                   bad_neighbours_threshold = 7, 
                   channel_threshold = 1, 
                   log = print, 
                   noise_mask_radius = 0 ):
    """
    This method will be applied to each pixel; it is at channel C.
    All neighbours should have their valye in the interval [C - epsilon, C + epsilon], or, if C = 0 or C = max, the neighbours could be wrapped to the previous/next order. 
    The final algorithm then considers the difference between the pixel and its neighbours' values, modulo the number of channels. If this results in a value above the channel_threshold, the neighbours is considered "bad".
    If a pixel has more than bad_neighbours_threshold "bad" neighbours, they are noisy and get value 1.
    Normal pixels get value 0.
    Returns the numpy array containing the binary noise map.
    
    Parameters:
    -----------
    - array is the numpy ndarray containing the data.
    - bad_neighbours_threshold is the number of neighbours with bad 
    values that the algorithm will tolerate. It defaults to 7.
    - channel_threshold is the channel distance that will be tolerated. 
    It defaults to 1.
    """
    start = time ( )

    noise_map = numpy.zeros ( shape = array.shape, dtype = numpy.int16 )
    max_channel = numpy.amax ( array )
    if ( max_channel == 0 ):
        return noise_map

    log ( "info: noise array 0% created." )
    last_percentage_logged = 0
    for x in range ( array.shape [ 0 ] ):
        percentage = 10 * int ( x / array.shape [ 0 ] * 10 )
        if ( percentage > last_percentage_logged ):
            log ( "info: noise array %d%% created." % ( percentage ) )
            last_percentage_logged = percentage

        for y in range ( array.shape [ 1 ] ):
            this_channel = array [ x ] [ y ]
            if ( this_channel != 0 ):
                continue

            neighbours = tuna.tools.get_pixel_neighbours ( ( x, y ), array )
            # Since pixels in the borders of the canvas have less neighbours,
            # they start with those non-existing neighbours marked as bad.
            number_of_neighbours = len ( neighbours )
            bad_results = 8 - number_of_neighbours
            for neighbour in neighbours:
                distance = abs ( array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] - this_channel )
                if distance > channel_threshold:
                    bad_results += 1
            if ( bad_results > bad_neighbours_threshold ):
                include_noise_circle ( position = ( x, y ), radius = noise_mask_radius, array = noise_map )
                continue
    log ( "info: noise array 100% created." )

    result = tuna.io.can ( log = log,
                           array = noise_map )

    log ( "info: create_noise_array() took %ds" % ( time ( ) - start ) )
    return result

def include_noise_circle ( position = ( int, int ), radius = int, array = numpy.array ):
    for x in range ( position[0] - ceil ( radius ), position[0] + ceil ( radius ) + 1 ):
        for y in range ( position[1] - ceil ( radius ), position[1] + ceil ( radius ) + 1 ):
            if position_is_valid_pixel_address ( position = ( x, y ), array = array ):
                if sqrt ( ( x - position[0] )**2 + ( y - position[1] )**2 ) <= radius:
                    array[x][y] = 1

def position_is_valid_pixel_address ( position = ( int, int ), array = numpy.array ):
    if ( position[0] >= 0 and
         position[0] < array.shape[0] and
         position[1] >= 0 and
         position[1] < array.shape[1] ):
        return True
    return False
