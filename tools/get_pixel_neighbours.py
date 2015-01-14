import numpy

def get_pixel_neighbours ( position = ( int, int ), array = numpy.ndarray ):
    result = []
    x = position[0]
    y = position[1]
    possible_neighbours = [ ( x-1, y+1 ), ( x, y+1 ), ( x+1, y+1 ),
                            ( x-1, y   ),             ( x+1, y   ),
                            ( x-1, y-1 ), ( x, y-1 ), ( x+1, y-1 ) ]

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
