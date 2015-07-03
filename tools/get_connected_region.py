import tuna

def get_connected_region ( point, array, already ):
    """
    Returns a list of all points that have the same value as point, and that are connected to it.
    Values come from array, and the array already will be updated with the points taken in consideration having the value 1, and ignoring all points that have value 1.
    """
    region = [ ]
    to_consider = [ point ]
    value = array [ point [ 0 ] ] [ point [ 1 ] ]
    
    while ( len ( to_consider ) != 0 ):
        here = to_consider.pop ( )
        region.append ( here )
        already [ here [ 0 ] ] [ here [ 1 ] ] = 1
        neighbours = tuna.tools.get_pixel_neighbours ( here, array )
        for neighbour in neighbours:
            pos_x = neighbour [ 0 ]
            pos_y = neighbour [ 1 ]
            if already [ pos_x ] [ pos_y ] == 1:
                continue
            if array   [ pos_x ] [ pos_y ] != value:
                continue
            to_consider.append ( neighbour )

    return region
