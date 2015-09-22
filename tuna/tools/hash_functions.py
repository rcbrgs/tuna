"""
This module's scope is related to hash operations.
"""

import hashlib

def get_hash_from_array ( array ):
    """
    This function will obtain a SHA1 hash from the input array by copying it in 'C' order, and then obtaining the hash.

    Parameters:

    - array, a numpy.ndarray.

    Returns a string, only containing hexadecimal digits.
    """
    hashable = array.copy ( order = 'C' )
    return hashlib.sha1 ( hashable ).hexdigest ( )
