#from math import floor, sqrt
import numpy
#from file_format import adhoc, file_reader, fits
#from gui import widget_viewer_2d
#from .orders import orders
from tools.get_pixel_neighbours import get_pixel_neighbours

def create_binary_noise_array ( bad_neighbours_threshold = 7, channel_threshold = 1, array = None, log = print ):
    """
    This method will be applied to each pixel; it is at channel C.
    All neighbours should be either in the same channel,
    in the channel C +- 1, or, if C = 0 or C = max, the neighbours
    could be at max or 0.
    Pixels that do not conform to this are noisy and get value 1.
    Normal pixels get value 0 and this produces a binary noise map.
    
    Parameters:
    -----------
    - bad_neighbours_threshold is the number of neighbours with bad 
    values that the algorithm will tolerate. It defaults to 7.
    - channel_threshold is the channel distance that will be tolerated. 
    It defaults to 1.
    """
    log ( "Producing binary noise map." )
    noise_map = numpy.zeros ( shape = array.shape )
    max_channel = numpy.amax ( array )
    for x in range ( array.shape[0] ):
        for y in range ( array.shape[1] ):
            this_channel = array[x][y]
            neighbours = get_pixel_neighbours ( ( x, y ), array )
            bad_results = 0
            for neighbour in neighbours:
                result = array[neighbour[0]][neighbour[1]] - this_channel
                other_result = this_channel + ( max_channel - array[neighbour[0]][neighbour[1]] )
                if result > other_result:
                    result = other_result
                if result > channel_threshold:
                    bad_results += 1
            if ( bad_results > bad_neighbours_threshold ):
                noise_map[x][y] = 1.0

    return noise_map
