"""This module's scope are tools related to geometry.

Example::

    >>> import tuna
    >>> tuna.tools.geometry.calculate_distance((0, 0), (10, 0))
    10.0
"""

import math

def calculate_distance(origin, destiny):
    """This function's goal is to calculate the euclidean distance between two
    points in a plane.

    Parameters:

    * origin : tuple of 2 floats

    * destiny : tuple of 2 floats

    Returns:

    *  : float

    """
    return math.sqrt((origin[0] - destiny[0])**2 +
                     (origin[1] - destiny[1])**2 )
