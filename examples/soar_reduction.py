#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

file_name = "/home/nix/sync/tuna/sample_data/soar_025_3D.fits"
o_raw = tuna.read ( file_name )
a_raw = o_raw.array
o_high_res = tuna.tools.phase_map.high_resolution ( f_airy_max_distance = 1904.325,
                                                    f_airy_min_distance = 1904,
                                                    array = a_raw,
                                                    f_calibration_wavelength = 6598.950,
                                                    f_free_spectral_range = 8.36522123894,
                                                    i_interference_order = 798,
                                                    f_interference_reference_wavelength = 6562.7797852,
                                                    wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array, 
                                                    channel_threshold = 1, 
                                                    bad_neighbours_threshold = 7, 
                                                    noise_mask_radius = 20,
                                                    f_scanning_wavelength = 6616.895 )

a_continuum              = o_high_res.get_continuum_array ( )
a_wrapped                = o_high_res.get_wrapped_phase_map_array ( )
a_noise                  = o_high_res.get_binary_noise_array ( )
a_distances              = o_high_res.get_borders_to_center_distances ( )
a_FSRs                   = o_high_res.get_order_array ( )
a_unwrapped              = o_high_res.get_unwrapped_phase_map_array ( )
a_parabolic_model        = o_high_res.get_parabolic_Polynomial2D_model ( )
a_airy                   = o_high_res.get_airy ( )
a_wavelength             = o_high_res.get_wavelength_calibrated ( )

tuna.io.write ( file_name   = file_name + '_0_raw.fits',
                array       = a_raw,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_1_continuum.fits',
                array       = a_continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_2_wrapped.fits',
                array       = a_wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_3_noise.fits',
                array       = a_noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_4_distances.fits',
                array       = a_distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_5_FSRs.fits',
                array       = a_FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_6_unwrapped.fits',
                array       = a_unwrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_7_parabolic_model.fits',
                array       = a_parabolic_model,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_8_airy_model.fits',
                array       = a_airy,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_9_wavelength_calibrated.fits',
                array       = a_wavelength,
                file_format = 'fits' )    

o_wavelength = tuna.read ( file_name + '_9_wavelength_calibrated.fits' )
o_unwrapped  = tuna.read ( file_name + '_6_unwrapped.fits' )

o_comparison = o_unwrapped - o_wavelength

tuna.write ( file_name   = file_name + '_9_wavelength_calibrated_residue.fits',
             array       = o_comparison.array,
             file_format = 'fits' )
