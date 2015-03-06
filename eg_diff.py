#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def compare_barycenter ( ):
    o_file       = tuna.io.read ( file_name = 'sample_data/g092_wrapped_barycenter.fits' )
    a_barycenter = o_file.get_array ( )
    a_cube       = tuna.data_cube.cube ( tan_data = a_barycenter )

    o_gold_file         = tuna.io.read ( file_name = 'sample_data/cal_bru.ad2' )
    a_gold              = o_gold_file.get_array ( )
    a_gold_cube         = tuna.data_cube.cube ( tan_data = a_gold )
    a_gold_flipped_cube = tuna.data_cube.flip ( s_axis = 'rows', o_cube = a_gold_cube )

    o_comparison         = tuna.data_cube.subtract ( o_cube_left = a_gold_cube, 
                                                     o_cube_right = a_cube )
    o_comparison_flipped = tuna.data_cube.subtract ( o_cube_left = a_gold_flipped_cube, 
                                                     o_cube_right = a_cube )

    tuna.io.write ( file_name   = 'gold_standard_comparison.fits',
                    array       = o_comparison.get_array ( ),
                    file_format = 'fits' )
    tuna.io.write ( file_name   = 'gold_standard_comparison_flipped.fits',
                    array       = o_comparison_flipped.get_array ( ),
                    file_format = 'fits' )
    
compare_barycenter ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
