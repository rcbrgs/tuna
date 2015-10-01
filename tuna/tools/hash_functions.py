"""
This module's scope is related to hash operations.

Example::

    >>> import tuna
    >>> import numpy
    >>> z = numpy.zeros ( shape = ( 2, 2 ) )
    >>> tuna.tools.get_hash_from_array ( z )
    'de8a847bff8c343d69b853a215e6ee775ef2ef96'
"""

import hashlib

def get_hash_from_array ( array ):
    """
    This function will obtain a SHA1 hash from the input array by copying it in 'C' order, and then obtaining the hash.

    Parameters:

    * array : numpy.ndarray

    Returns:

    * string
        This hash string only contains hexadecimal digits.
    """
    hashable = array.copy ( order = 'C' )
    return hashlib.sha1 ( hashable ).hexdigest ( )
