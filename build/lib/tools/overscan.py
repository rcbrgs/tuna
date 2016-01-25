"""
This module's scope are operations related to removing overscan from datacubes.
"""

__version__ = "0.1.0"
__changelog = {
    "0.1.0" : { "Tuna" : "0.15.0", "Change" : "Initial commit." }
}

import numpy
import tuna

def no_overscan ( data : tuna.io.can,
                  elements_to_remove : dict = { } ) -> tuna.io.can:
    """
    This function's goal is to simply return the input data unaltered; it is meant as a passthrough procedure to be used as the overscan plugin when no overscan removal is needed.

    Arguments:

    * data : tuna.io.can

    * elements_to_remove : dict : { }
        An empty argument, which is necessary to obey the signature for this plugin.

    Returns:

    * tuna.io.can
        The same data as the input.
    """
    return data

def remove_elements ( data : tuna.io.can,
                      elements_to_remove : dict ) -> tuna.io.can:
    """
    This function's goal is to remove some columns from the input datacube. This will result in an output that has different dimensions than the input.

    Arguments:

    * data : tuna.io.can
        The data cube.

    * elements_to_remove : dict
        A dictionary of elements that are to be removed from the data cube. Each key in this dictionary is the axis of the elements to be removed, and the value associated to this key should be a list of the elements to remove. For example, to remove columns 1 and 2, and row 13 of the input 'data', this argument should be { 1 : [ 13 ], 2 : [ 1, 2 ] }. (The apparent discrepancy between the axis numbering and the "row index is the last" rule comes from numpy.where.

    Returns:

    * tuna.io.can
        The original data, minus the elements passed in the argument 'elements_to_remove'.
    """
    result_array = numpy.copy ( data.array )
    for key in elements_to_remove.keys ( ):
        result_array = numpy.delete ( result_array, elements_to_remove [ key ], key )
    return tuna.io.can ( array = result_array )
