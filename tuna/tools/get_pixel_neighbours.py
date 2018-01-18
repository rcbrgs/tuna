"""This module's scope are algorithms related to obtaining the list of neighbours for a given position in an array.

Example:

    >>> import tuna
    >>> import numpy
    >>> z = numpy.zeros(shape = (30, 30))
    >>> tuna.tools.get_pixel_neighbours(position = (10, 20), array = z)
    [(9, 19), (9, 20), (9, 21), (10, 19), (10, 21), (11, 19), (11, 20), (11, 21)]
"""
__version__ = "0.1.2"
__changelog = {
    "0.1.2": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.1": {"Tuna": "0.14.0", "Change": "updated documentation to new style."},
    "0.1.0": {"Change": "Added distance_threshold_parameter, so users can get " \
              "neighbours with arbitrary distance."}
}

import numpy

def get_pixel_neighbours(position = (int, int),
                         array = numpy.ndarray, distance_threshold = 1 ):
    """Produce a list of tuples of 2 integers where each tuple encodes the
    position of a neighbour of the input position in the input array.

    Parameters:

    * position : tuple of 2 integers

    * array : numpy.ndarray

    * distance_threshold : integer : 1
    """
    
    result = []
    x = position[0]
    y = position[1]

    for col in range(position[0] - distance_threshold,
                     position[0] + distance_threshold + 1):
        for row in range(position[1] - distance_threshold,
                         position[1] + distance_threshold + 1):
            if (col, row) == position:
                continue
            try:
                possible_neighbours.append((col, row))
            except UnboundLocalError:
                possible_neighbours = [(col, row)]

    def is_valid_position(position = (int, int), array = numpy.ndarray):
        if (position[0] >= 0 and 
            position[0] < array.shape[0]):
            if position[1] >= 0 and position[1] < array.shape[1]:
                return True
        return False

    for possibility in possible_neighbours:
        if is_valid_position(position = possibility, array = array):
            result.append(possibility)
                
    return result
