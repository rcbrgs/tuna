#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

file_name = "/home/nix/sync/tuna/sample_data/G094.AD3"
file_name_unpathed = file_name.split ( "/" ) [ -1 ]

can = tuna.read ( file_name )
raw = can.array
high_res = tuna.tools.phase_map.high_resolution ( array = raw,
                                                  beam = 450,
                                                  calibration_wavelength = 6598.950,
                                                  finesse = 15.,
                                                  focal_length = 0.1,
                                                  free_spectral_range = 8.36522123894,
                                                  gap = 1904,
                                                  interference_order = 798,
                                                  interference_reference_wavelength = 6562.7797852,
                                                  wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array, 
                                                  channel_threshold = 1, 
                                                  bad_neighbours_threshold = 7, 
                                                  noise_mask_radius = 7,
                                                  scanning_wavelength = 6616.895 )

continuum              = high_res.get_continuum_array ( )
filtered               = high_res.get_filtered ( )
wrapped                = high_res.get_wrapped_phase_map_array ( )
noise                  = high_res.get_binary_noise_array ( )
distances              = high_res.get_borders_to_center_distances ( )
FSRs                   = high_res.get_order_array ( )
unwrapped              = high_res.get_unwrapped_phase_map_array ( )
parabolic_model        = high_res.get_parabolic_Polynomial2D_model ( )
airy                   = high_res.get_airy ( )
wavelength             = high_res.get_wavelength_calibrated ( )

tuna.io.write ( file_name   = file_name_unpathed + '_00_raw.fits',
                array       = raw,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_01_continuum.fits',
                array       = continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_02_filtered.fits',
                array       = filtered,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_03_wrapped.fits',
                array       = wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_04_noise.fits',
                array       = noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_05_distances.fits',
                array       = distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_06_FSRs.fits',
                array       = FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_07_unwrapped.fits',
                array       = unwrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_08_parabolic_model.fits',
                array       = parabolic_model,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_09_airy_model.fits',
                array       = airy,
                file_format = 'fits' )    
tuna.io.write ( file_name   = file_name_unpathed + '_10_wavelength_calibrated.fits',
                array       = wavelength,
                file_format = 'fits' )    
