#!/bin/env ipython3

import tuna

can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3_second_ring_ROI.fits' )
raw = can.array
high_res = tuna.tools.phase_map.high_resolution ( array = raw,
                                                  beam = 450,
                                                  bad_neighbours_threshold = 7,
                                                  calibration_wavelength = 6598.950,
                                                  channel_threshold = 1, 
                                                  finesse = 15,
                                                  focal_length = 0.1,
                                                  free_spectral_range = 8.36522123894,
                                                  gap = 1904,
                                                  interference_order = 798,
                                                  interference_reference_wavelength = 6562.7797852,
                                                  noise_mask_radius = 7,
                                                  scanning_wavelength = 6616.895,
                                                  wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )

continuum = high_res.get_continuum_array ( )
wrapped   = high_res.get_wrapped_phase_map_array ( )
noise     = high_res.get_binary_noise_array ( )
distances = high_res.get_borders_to_center_distances ( )
FSRs      = high_res.get_order_array ( )
unwrapped = high_res.get_unwrapped_phase_map_array ( )

tuna.io.write ( file_name   = '1_g092_continuum.fits',
                array       = continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '2_g092_wrapped_barycenter.fits',
                array       = wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '3_g092_binary_noise.fits',
                array       = noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '4_g092_borders_center_distances.fits',
                array       = distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '5_g092_orders.fits',
                array       = FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = '6_g092_unwrapped_phase_map.fits',
                array       = unwrapped,
                file_format = 'fits' )    
