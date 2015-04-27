#!/bin/env ipython3

import tuna

can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3_second_ring_ROI.fits' )
high_res = tuna.tools.phase_map.high_resolution ( beam = 450,
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
                                                  tuna_can = can )

continuum = high_res.continuum
wrapped   = high_res.wrapped_phase_map
noise     = high_res.noise
distances = high_res.borders_to_center_distances
FSRs      = high_res.order_map
unwrapped = high_res.unwrapped_phase_map

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
