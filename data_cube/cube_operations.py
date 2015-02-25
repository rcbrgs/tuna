"""
Responsible for obtaining the difference between two data cubes.
"""

from .cube import cube
import numpy

def flip ( s_axis = None,
           log = print,
           o_cube = None ):
    """
    Returns a data cube that has the entries along the axis dimension flipped.
    """
    if ( s_axis != None and
         o_cube != None ):
        tan_result = numpy.ndarray ( shape = o_cube.get_array ( ) . shape )
        i_plane_mod = 0
        i_row_mod = 0
        i_col_mod = 0
        if ( s_axis.lower ( ) == 'planes' ):
            i_plane_mod = o_cube.get_planes ( ) - 1
        elif ( s_axis.lower ( ) == 'rows' ): 
            i_row_mod = o_cube.get_rows ( ) - 1
        else:
            i_col_mod = o_cube.get_cols ( ) - 1
        
        for i_plane in o_cube.get_planes_range ( ):
            for i_row in o_cube.get_rows_range ( ):
                for i_col in o_cube.get_cols_range ( ):
                    tan_result [ i_plane_mod - i_plane ] [ i_row_mod - i_row ] [ i_col_mod - i_col ] = o_cube.get_array ( ) [ i_plane ] [ i_row ] [ i_col ] 
        return cube ( log = log, tan_data = tan_result )

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
        log ( "o_cube_left.get_array ( ).shape = %s, o_cube_right.get_array ( ).shape = %s" % ( o_cube_left.get_array ( ).shape, o_cube_right.get_array ( ).shape ) )

    tan_left = o_cube_left.get_array ( )
    tan_right = o_cube_right.get_array ( )
    tan_comparison = numpy.ndarray ( shape = ( o_cube_left.get_planes ( ),
                                               o_cube_left.get_rows ( ),
                                               o_cube_left.get_cols ( ) ) )

    tan_comparison = tan_left - tan_right

    return cube ( log = log, tan_data = tan_comparison )
