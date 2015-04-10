#!/bin/env ipython3

import numpy
import tuna

raw = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
continuum = tuna.tools.phase_map.create_continuum_array ( array = raw.array )
discontinuum = raw.array - continuum
wrapped = tuna.tools.phase_map.create_barycenter_array ( array = discontinuum )
center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( wrapped = wrapped )

airy = tuna.tools.models.fit_airy ( beam = 450,
                                    center = center,
                                    finesse = 15.,
                                    focal_length = 0.1,
                                    gap = 1904,
                                    discontinuum = discontinuum )

def generate_data ( channels ):
    suppressed = tuna.tools.phase_map.suppress_channel ( array = raw.array, 
                                                         replacement = airy,
                                                         channels = channels )
    channel_string = ""
    for channel in channels:
        channel_string += str ( channel ) + "_"

    tuna.io.write ( file_name   = 'G094.AD3_channel_suppressed_' + channel_string + '04_suppressed.fits',
                    array       = suppressed,
                    file_format = 'fits' )    

    file_name = "G094.AD3_channel_suppressed_" + channel_string + '04_suppressed.fits'
    file_name_unpathed = file_name.split ( "/" ) [ -1 ]

    o_raw = tuna.read ( file_name )
    a_raw = o_raw.array
    o_high_res = tuna.tools.phase_map.high_resolution ( array = a_raw,
                                                        beam = 450,
                                                        f_calibration_wavelength = 6598.950,
                                                        finesse = 15.,
                                                        focal_length = 0.1,
                                                        f_free_spectral_range = 8.36522123894,
                                                        gap = 1904,
                                                        i_interference_order = 798,
                                                        f_interference_reference_wavelength = 6562.7797852,
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array, 
                                                        channel_threshold = 1, 
                                                        bad_neighbours_threshold = 7, 
                                                        noise_mask_radius = 7,
                                                        f_scanning_wavelength = 6616.895 )

    a_continuum              = o_high_res.get_continuum_array ( )
    a_filtered               = o_high_res.get_filtered ( )
    a_wrapped                = o_high_res.get_wrapped_phase_map_array ( )
    a_noise                  = o_high_res.get_binary_noise_array ( )
    a_distances              = o_high_res.get_borders_to_center_distances ( )
    a_FSRs                   = o_high_res.get_order_array ( )
    a_unwrapped              = o_high_res.get_unwrapped_phase_map_array ( )
    a_parabolic_model        = o_high_res.get_parabolic_Polynomial2D_model ( )
    a_airy                   = o_high_res.get_airy ( )
    a_wavelength             = o_high_res.get_wavelength_calibrated ( )

    tuna.io.write ( file_name   = file_name_unpathed + '_07_unwrapped.fits',
                    array       = a_unwrapped,
                    file_format = 'fits' )    

    import numpy
    compare_one = tuna.io.read ( file_name = file_name_unpathed + '_07_unwrapped.fits' )
    compare_two = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_07_unwrapped.fits' )

    comparison = compare_one.array - compare_two.array
    tuna.io.write ( file_name   = file_name_unpathed + '_11_comparison.fits',
                    array       = comparison,
                    file_format = 'fits' )



generate_data ( [ 0 ] )
generate_data ( [ 0, 1 ] )
generate_data ( [ 0, 1, 2 ] )
generate_data ( [ 0, 1, 2, 3 ] )
generate_data ( [ 0, 1, 2, 3, 4 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34 ] )
generate_data ( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 ] )

