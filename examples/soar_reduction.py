#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

file_name = "/home/nix/sync/tuna/sample_data/soar_025_3D.fits"
can = tuna.read ( file_name )
raw = raw.array
high_res = tuna.tools.phase_map.high_resolution ( airy_max_distance = 1904.325,
                                                  airy_min_distance = 1904,
                                                  array = a_raw,
                                                  calibration_wavelength = 6598.950,
                                                  free_spectral_range = 8.36522123894,
                                                  interference_order = 798,
                                                  interference_reference_wavelength = 6562.7797852,
                                                  wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array, 
                                                  channel_threshold = 1, 
                                                  bad_neighbours_threshold = 7, 
                                                  noise_mask_radius = 20,
                                                  scanning_wavelength = 6616.895 )

continuum              = high_res.get_continuum_array ( )
wrapped                = high_res.get_wrapped_phase_map_array ( )
noise                  = high_res.get_binary_noise_array ( )
distances              = high_res.get_borders_to_center_distances ( )
FSRs                   = high_res.get_order_array ( )
unwrapped              = high_res.get_unwrapped_phase_map_array ( )
parabolic_model        = high_res.get_parabolic_Polynomial2D_model ( )
airy                   = high_res.get_airy ( )
wavelength             = high_res.get_wavelength_calibrated ( )

tuna.io.write ( file_name   = file_name + '_0_raw.fits',
                array       = raw,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_1_continuum.fits',
                array       = continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_2_wrapped.fits',
                array       = wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_3_noise.fits',
                array       = noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_4_distances.fits',
                array       = distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_5_FSRs.fits',
                array       = FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_6_unwrapped.fits',
                array       = unwrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_7_parabolic_model.fits',
                array       = parabolic_model,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_8_airy_model.fits',
                array       = airy,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name + '_9_wavelength_calibrated.fits',
                array       = wavelength,
                file_format = 'fits' )    

wavelength = tuna.read ( file_name + '_9_wavelength_calibrated.fits' )
unwrapped  = tuna.read ( file_name + '_6_unwrapped.fits' )

comparison = unwrapped - wavelength

tuna.write ( file_name   = file_name + '_9_wavelength_calibrated_residue.fits',
             array       = comparison.array,
             file_format = 'fits' )
