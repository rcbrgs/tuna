#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def compare_barycenter ( ):
    o_barycenter_file      = tuna.io.read ( file_name = '2_wrapped.fits' )
    a_barycenter           = o_barycenter_file.get_array ( )
    o_barycenter_gold_file = tuna.io.read ( file_name = 'sample_data/cal_bru.ad2' )
    a_barycenter_gold      = o_barycenter_gold_file.get_array ( )
    import numpy
    a_comparison = numpy.ndarray ( shape = a_barycenter.shape )
    for i_row in range ( a_comparison.shape[0] ):
        for i_col in range ( a_comparison.shape[1] ):
            # If the comparison seem to be "shifted" vertically between gold and result, change following line:
            #a_comparison [ i_row ] [ i_col ] = ( a_barycenter_gold [ a_comparison.shape[0] - 1 - i_row ] [ i_col ] - 
            a_comparison [ i_row ] [ i_col ] = ( a_barycenter_gold [ i_row ] [ i_col ] - 
                                                 a_barycenter [ i_row ] [ i_col ] )

    tuna.io.write ( file_name   = '8_wrapped_comparison.fits',
                    array       = a_comparison,
                    file_format = 'fits' )
    
def unwrap_phase_map ( ):
    o_raw_file = tuna.io.read ( file_name = 'sample_data/G092.AD3' )
    a_raw      = o_raw_file.get_array ( )
    o_high_res = tuna.tools.phase_map.high_resolution ( array = a_raw,
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array, 
                                                        channel_threshold = 1, 
                                                        bad_neighbours_threshold = 7, 
                                                        noise_mask_radius = 7 )
    a_continuum              = o_high_res.get_continuum_array ( )
    a_wrapped                = o_high_res.get_wrapped_phase_map_array ( )
    a_noise                  = o_high_res.get_binary_noise_array ( )
    a_distances              = o_high_res.get_borders_to_center_distances ( )
    a_FSRs                   = o_high_res.get_order_array ( )
    a_unwrapped              = o_high_res.get_unwrapped_phase_map_array ( )
    a_parabolic_model        = o_high_res.get_parabolic_Polynomial2D_model ( )

    tuna.io.write ( file_name   = '0_raw.fits',
                    array       = a_raw,
                    file_format = 'fits' )    
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
    tuna.io.write ( file_name   = '7_parabolic_model.fits',
                    array       = a_parabolic_model,
                    file_format = 'fits' )    

    t_parabolic_coefficients = o_high_res.get_parabolic_Polynomial2D_coefficients ( )
    print ( "Parabolic model coefficients = %s" % str ( t_parabolic_coefficients ) )

unwrap_phase_map ( )
compare_barycenter ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
