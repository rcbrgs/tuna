"""
Scope: create and handle hash operations.
"""

import hashlib

def get_hash_from_array ( array ):
    hashable = array.copy ( order = 'C' )
    return hashlib.sha1 ( hashable ).hexdigest ( )
