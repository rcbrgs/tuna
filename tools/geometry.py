import math

def calculate_distance ( origin, destiny ):
    """
    This function will calculate the euclidean distance between two points in a plane.

    Parameters:

    - origin, a tuple of 2 floats;
    - destiny, a tuple of 2 floats.

    Returns a float.
    """
    return math.sqrt ( ( origin [ 0 ] - destiny [ 0 ] ) ** 2 +
                       ( origin [ 1 ] - destiny [ 1 ] ) ** 2 )
