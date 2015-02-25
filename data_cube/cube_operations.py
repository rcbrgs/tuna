"""
Responsible for obtaining the difference between two data cubes.
"""

from .cube import cube
import numpy

def subtract ( log = print,
               o_cube_left = cube, 
               o_cube_right = cube ):
    """
    Returns o_cube_left - o_cube_right
    """
   
    if ( o_cube_left.get_planes ( ) != o_cube_right.get_planes ( ) or
         o_cube_left.get_rows ( ) != o_cube_right.get_rows ( ) or
         o_cube_left.get_cols ( ) != o_cube_right.get_cols ( ) ):
        log ( "Cubes have different dimensionality, cannot substract." )

    tan_left = o_cube_left.get_array ( )
    tan_right = o_cube_right.get_array ( )
    tan_comparison = numpy.ndarray ( shape = ( o_cube_left.get_planes ( ),
                                               o_cube_left.get_rows ( ),
                                               o_cube_left.get_cols ( ) ) )

    tan_comparison = tan_left - tan_right

    return cube ( log = log, tan_data = tan_comparison )
