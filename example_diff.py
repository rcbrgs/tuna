#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def g092_compare_barycenter ( ):
    g092_barycenter_file = tuna.io.read ( file_name = '2_g092_wrapped_barycenter.fits' )
    g092_barycenter_array = g092_barycenter_file.get_array ( )
    g092_barycenter_cube = tuna.data_cube.cube ( tan_data = g092_barycenter_array )

    g092_barycenter_gold_file = tuna.io.read ( file_name = 'examples/cal_bru.ad2' )
    g092_barycenter_gold_array = g092_barycenter_gold_file.get_array ( )
    g092_barycenter_gold_cube = tuna.data_cube.cube ( tan_data = g092_barycenter_gold_array )
    g092_barycenter_gold_flipped_cube = tuna.data_cube.flip ( s_axis = 'rows', o_cube = g092_barycenter_gold_cube )

    o_comparison = tuna.data_cube.subtract ( o_cube_left = g092_barycenter_gold_cube, o_cube_right = g092_barycenter_cube )

    tuna.io.write ( file_name   = '7_g092_gold_standard_comparison.fits',
                    array       = o_comparison.get_array ( ),
                    file_format = 'fits' )
    
def g092_unwrap_phase_map ( ):
    g092_raw_file = tuna.io.read ( file_name = 'examples/G092.AD3' )
    g092_array = g092_raw_file.get_array ( )
    high_res_FP_phase_map_tool = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( array = g092_array,wrapped_phase_map_algorithm = tuna.tools.phase_map_creation.create_barycenter_array, channel_threshold = 1, bad_neighbours_threshold = 7, noise_mask_radius = 7 )
    g092_wrapped_array = high_res_FP_phase_map_tool.get_wrapped_phase_map_array ( )
    g092_continuum_array = high_res_FP_phase_map_tool.get_continuum_array ( )
    g092_unwrapped_array = high_res_FP_phase_map_tool.get_unwrapped_phase_map_array ( )
    g092_binary_noise_array = high_res_FP_phase_map_tool.get_binary_noise_array ( )
    g092_borders_to_center_distances = high_res_FP_phase_map_tool.get_borders_to_center_distances ( )
    g092_order_array = high_res_FP_phase_map_tool.get_order_array ( )

    tuna.io.write ( file_name   = '1_g092_continuum.fits',
                    array       = g092_continuum_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '2_g092_wrapped_barycenter.fits',
                    array       = g092_wrapped_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '3_g092_binary_noise.fits',
                    array       = g092_binary_noise_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '4_g092_borders_center_distances.fits',
                    array       = g092_borders_to_center_distances,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '5_g092_orders.fits',
                    array       = g092_order_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '6_g092_unwrapped_phase_map.fits',
                    array       = g092_unwrapped_array,
                    file_format = 'fits' )    

#g092_unwrap_phase_map ( )
g092_compare_barycenter ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
