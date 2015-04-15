"""
Responsible for obtaining the difference between two data cubes.
"""

from .cube import cube
import numpy

def flip ( axis = None,
           log = print,
           data_cube = None ):
    """
    Returns a data cube that has the entries along the axis dimension flipped.
    """
    if ( axis != None and
         data_cube != None ):
        result = numpy.ndarray ( shape = data_cube.get_array ( ) . shape )
        plane_mod = 0
        row_mod = 0
        col_mod = 0
        if ( axis.lower ( ) == 'planes' ):
            plane_mod = data_cube.get_planes ( ) - 1
        elif ( axis.lower ( ) == 'rows' ): 
            row_mod = data_cube.get_rows ( ) - 1
        else:
            col_mod = data_cube.get_cols ( ) - 1
        
        for plane in data_cube.get_planes_range ( ):
            for row in data_cube.get_rows_range ( ):
                for col in data_cube.get_cols_range ( ):
                    result [ plane_mod - plane ] [ row_mod - row ] [ col_mod - col ] = data_cube.get_array ( ) [ plane ] [ row ] [ col ] 
        return cube ( log = log, tan_data = result )

def subtract ( log = print,
               data_cube_left = cube, 
               data_cube_right = cube ):
    """
    Returns data_cube_left - data_cube_right
    """
   
    if ( data_cube_left.get_planes ( ) != data_cube_right.get_planes ( ) or
         data_cube_left.get_rows ( ) != data_cube_right.get_rows ( ) or
         data_cube_left.get_cols ( ) != data_cube_right.get_cols ( ) ):
        log ( "Cubes have different dimensionality, cannot substract." )
        log ( "data_cube_left.get_array ( ).shape = %s, data_cube_right.get_array ( ).shape = %s" % ( data_cube_left.get_array ( ).shape, data_cube_right.get_array ( ).shape ) )

    left = data_cube_left.get_array ( )
    right = data_cube_right.get_array ( )
    comparison = numpy.ndarray ( shape = ( data_cube_left.get_planes ( ),
                                           data_cube_left.get_rows ( ),
                                           data_cube_left.get_cols ( ) ) )

    comparison = left - right

    return cube ( log = log, tan_data = comparison )
