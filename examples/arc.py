#!/bin/env ipython3

import tuna

o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3_second_ring_ROI.fits' )
a_raw = o_file.array
o_high_res = tuna.tools.phase_map.high_resolution ( array = a_raw,
                                                    bad_neighbours_threshold = 7,
                                                    channel_threshold = 1, 
                                                    noise_mask_radius = 7,
                                                    wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )
a_continuum = o_high_res.get_continuum_array ( )
a_wrapped   = o_high_res.get_wrapped_phase_map_array ( )
a_noise     = o_high_res.get_binary_noise_array ( )
a_distances = o_high_res.get_borders_to_center_distances ( )
a_FSRs      = o_high_res.get_order_array ( )
a_unwrapped = o_high_res.get_unwrapped_phase_map_array ( )

tuna.io.write ( file_name   = '1_g092_continuum.fits',
                array       = a_continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '2_g092_wrapped_barycenter.fits',
                array       = a_wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '3_g092_binary_noise.fits',
                array       = a_noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '4_g092_borders_center_distances.fits',
                array       = a_distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '5_g092_orders.fits',
                array       = a_FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '6_g092_unwrapped_phase_map.fits',
                array       = a_unwrapped,
                file_format = 'fits' )    
