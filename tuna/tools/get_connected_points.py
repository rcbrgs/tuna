import tuna

def get_connected_points ( position, array ):
    """
    This function returns a list of tuples of 2 integers, each one encoding the coordinates for pixels in the input array that have the same value as the one store at the input position, and that have a "direct path" to the position that only contain pixels with the same value.

    Parameters:

    - position, a tuple of 2 integers;
    - array, a numpy.ndarray containing the data.
    """
    to_verify = [ position ]
    verified = [ ]
    value = array [ position [ 0 ] ] [ position [ 1 ] ]

    while ( len ( to_verify ) != 0 ):
        current = to_verify.pop ( )
        if array [ current [ 0 ] ] [ current [ 1 ] ] == value:
            verified.append ( current )
            neighbours = tuna.tools.get_pixel_neighbours ( position, array )
            for neighbour in neighbours:
                if neighbour not in verified:
                    to_verify.append ( neighbour )

    return verified
