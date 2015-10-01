# -*- coding: utf-8 -*-
"""
This module's scope are tools relying on numpy.percentile.

Example::

    >>> import numpy
    >>> import tuna
    >>> data = numpy.zeros ( shape = ( 10, 100, 100 ) )
    >>> tuna.tools.find_lowest_nonnull_percentile ( data )
    1
    >>> data [ 0, :, : ] = numpy.ones ( shape = ( 100, 100 ) )
    >>> tuna.tools.find_lowest_nonnull_percentile ( data )
    90
"""

import numpy

def find_lowest_nonnull_percentile ( array ):
    """
    This function will attempt to find the lowest value, starting at 1, which makes numpy.percentile return a non-null value when fed the input array.

    Parameters:

    * array : numpy.ndarray
        Containing the data to apply the percentile to.

    Returns:

    * lower_percentile : integer
        The lowest percentile that is not null; if all data is null, this return value will be 1.
    """
    lower_percentile = 1
    lower_percentile_value = numpy.percentile ( array, lower_percentile )
    while ( lower_percentile_value <= 0 ):
        lower_percentile += 1
        if lower_percentile == 100:
            lower_percentile = 1
            break
        lower_percentile_value = numpy.percentile ( array, lower_percentile )

    return lower_percentile
