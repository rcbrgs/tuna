import numpy

def get_pixel_neighbours ( position = ( int, int ), array = numpy.ndarray, distance_threshold = 1 ):
    __version__ = '0.1.0'
    changelog = {
        '0.1.0' : "Added distance_threshold_parameter, so users can get neighbours with arbitrary distance."
        }
    
    result = [ ]
    x = position [ 0 ]
    y = position [ 1 ]

    for col in range ( position [ 0 ] - distance_threshold, position [ 0 ] + distance_threshold + 1 ):
        for row in range ( position [ 1 ] - distance_threshold, position [ 1 ] + distance_threshold + 1 ):
            if ( col, row ) == position:
                continue
            try:
                possible_neighbours.append ( ( col, row ) )
            except UnboundLocalError:
                possible_neighbours = [ ( col, row ) ]

    def is_valid_position ( position = ( int, int ), array = numpy.ndarray ):
        if ( position[0] >= 0 and 
             position[0] < array.shape[0] ):
            if position[1] >= 0 and position[1] < array.shape[1]:
                return True
        return False

    for possibility in possible_neighbours:
        if is_valid_position ( position = possibility, array = array ):
            result.append ( possibility )
                
    return result
