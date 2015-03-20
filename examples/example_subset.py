#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna.init ( )

# User-specific code would go here.
def channel_subset ( ):
    o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
    a_raw  = o_file.get_array ( )

    o_high_res = tuna.tools.phase_map.high_resolution ( array = a_raw, 
                                                        channel_threshold = 1, 
                                                        bad_neighbours_threshold = 7, 
                                                        # no channel 20
                                                        #il_channel_subset = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 ],
                                                        # no channels 20 and 21
                                                        #il_channel_subset = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 ],
                                                        # no channels 20, 21 and 22
                                                        il_channel_subset = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 ],
                                                        noise_mask_radius = 7,
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )

    a_wrapped       = o_high_res.get_wrapped_phase_map_array ( )
    a_continuum     = o_high_res.get_continuum_array ( )
    a_noise         = o_high_res.get_binary_noise_array ( )
    a_distances     = o_high_res.get_borders_to_center_distances ( )
    a_FSRs          = o_high_res.get_order_array ( )
    a_unwrapped     = o_high_res.get_unwrapped_phase_map_array ( )
    a_parabolic_fit = o_high_res.get_parabolic_Polynomial2D_model ( )

    tuna.io.write ( file_name   = '1_continuum.fits',
                    array       = a_continuum,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '2_wrapped.fits',
                    array       = a_wrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '3_noise.fits',
                    array       = a_noise,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '4_distances.fits',
                    array       = a_distances,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '5_FSRs.fits',
                    array       = a_FSRs,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '6_unwrapped.fits',
                    array       = a_unwrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '7_parabolic_fit.fits',
                    array       = a_parabolic_fit,
                    file_format = 'fits' )

def compare_barycenter ( ):
    o_file       = tuna.io.read ( file_name = '6_unwrapped.fits' )
    a_barycenter = o_file.get_array ( )
    a_cube       = tuna.data_cube.cube ( tan_data = a_barycenter )

    o_gold_file         = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/g094_tuna_unwrapped.fits' )
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
    
channel_subset ( )
compare_barycenter ( )

# This call is required to close the daemons gracefully:
tuna.finish ( )
