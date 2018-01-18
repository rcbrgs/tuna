"""This module's scope are algorithms to obtain connected regions of a array.

Example::

    >>> import tuna
    >>> import numpy
    >>> z = numpy.zeros(shape = (2, 2))
    >>> tuna.tools.get_connected_points((1, 1), z)
    [(1, 1), (1, 0), (0, 1), (0, 0), (0, 0), (0, 1), (0, 0)]
"""

import tuna

def get_connected_points(position, array):
    """Generate a list of the coordinates for pixels in the input array that have
    the same value as the one store at the input position, and that have a
    "direct path" to the position that only contain pixels with the same value.

    Parameters:

    * position : tuple of 2 integers
        The position of the seed of the region.

    * array : numpy.ndarray

    Returns:

    * list of tuples of 2 integers each.
    """
    to_verify = [position]
    verified = []
    value = array[position[0]][position[1]]

    while (len(to_verify) != 0):
        current = to_verify.pop()
        if array[current[0]][current[1]] == value:
            verified.append(current)
            neighbours = tuna.tools.get_pixel_neighbours(position, array)
            for neighbour in neighbours:
                if neighbour not in verified:
                    to_verify.append(neighbour)

    return verified
