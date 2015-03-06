#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def create_ROI_examples ( ):

    o_file = tuna.io.read ( file_name = 'sample_data/G092.AD3' )
    a_raw = o_file.get_array ( )

    import numpy
    a_center_ROI    = numpy.ndarray ( shape = ( a_raw.shape[0], 100, 100 ) )
    a_offcenter_ROI = numpy.ndarray ( shape = ( a_raw.shape[0], 100, 100 ) )
    a_rings_ROI     = numpy.ndarray ( shape = ( a_raw.shape[0], 400, 400 ) )

    for i_row in range ( 100 ):
        for i_col in range ( 100 ):
            for i_dep in range ( a_raw.shape [ 0 ] ):
                a_center_ROI    [ i_dep ] [ i_row ] [ i_col ] = a_raw [ i_dep ] [ i_row + 170 ] [ i_col + 200 ]
                a_offcenter_ROI [ i_dep ] [ i_row ] [ i_col ] = a_raw [ i_dep ] [ i_row + 100 ] [ i_col + 100 ]

    for i_row in range ( 400 ):
        for i_col in range ( 400 ):
            for i_dep in range ( a_raw.shape [ 0 ] ):
                    a_rings_ROI [ i_dep ] [ i_row ] [ i_col ] = a_raw [ i_dep ] [ i_row ] [ i_col ]

    tuna.io.write ( file_name   = 'center_ROI_1_raw.fits',
	            array       = a_center_ROI, 
		    metadata    = [],
		    file_format = 'fits' )
    tuna.io.write ( file_name   = 'offcenter_ROI_1_raw.fits',
	            array       = a_offcenter_ROI, 
		    metadata    = [],
		    file_format = 'fits' )
    tuna.io.write ( file_name   = 'rings_ROI_1_raw.fits',
	            array       = a_rings_ROI, 
		    metadata    = [],
		    file_format = 'fits' )

def process_ROI_examples ( ):
    o_center_ROI_file = tuna.io.read ( file_name = 'center_ROI_1_raw.fits' )
    a_center_ROI_raw = o_center_ROI_file.get_array ( )
    o_high_res = tuna.tools.phase_map.high_resolution ( array = a_center_ROI_raw,
                                                        bad_neighbours_threshold = 7, 
                                                        channel_threshold = 1, 
                                                        noise_mask_radius = 7,
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )
    a_center_ROI_continuum = o_high_res.get_continuum_array ( )
    a_center_ROI_wrapped   = o_high_res.get_wrapped_phase_map_array ( )
    a_center_ROI_noise     = o_high_res.get_binary_noise_array ( )
    a_center_ROI_distances = o_high_res.get_borders_to_center_distances ( )
    a_center_ROI_FSRs      = o_high_res.get_order_array ( )
    a_center_ROI_unwrapped = o_high_res.get_unwrapped_phase_map_array ( )

    tuna.io.write ( file_name   = 'center_ROI_2_continuum.fits',
                    array       = a_center_ROI_continuum,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'center_ROI_3_wrapped_phase_map_barycenter.fits',
                    array       = a_center_ROI_wrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'center_ROI_4_binary_noise.fits',
                    array       = a_center_ROI_noise,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'center_ROI_5_ring_borders.fits',
                    array       = a_center_ROI_distances,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'center_ROI_6_orders.fits',
                    array       = a_center_ROI_FSRs,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'center_ROI_7_unwrapped_phase_map.fits',
                    array       = a_center_ROI_unwrapped,
                    file_format = 'fits' )    

    o_offcenter_file = tuna.io.read ( file_name = 'offcenter_ROI_1_raw.fits' )
    a_offcenter_raw = o_offcenter_file.get_array ( )
    o_high_res = tuna.tools.phase_map.high_resolution ( array = a_offcenter_raw,
                                                        bad_neighbours_threshold = 7, 
                                                        channel_threshold = 1, 
                                                        noise_mask_radius = 7, 
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )

    a_offcenter_continuum = o_high_res.get_continuum_array ( )
    a_offcenter_wrapped   = o_high_res.get_wrapped_phase_map_array ( )
    a_offcenter_noise     = o_high_res.get_binary_noise_array ( )
    a_offcenter_distances = o_high_res.get_borders_to_center_distances ( )
    a_offcenter_FSRs      = o_high_res.get_order_array ( )
    a_offcenter_unwrapped = o_high_res.get_unwrapped_phase_map_array ( )

    tuna.io.write ( file_name   = 'offcenter_ROI_2_continuum.fits',
                    array       = a_offcenter_continuum,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'offcenter_ROI_3_wrapped_phase_map_barycenter.fits',
                    array       = a_offcenter_wrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'offcenter_ROI_4_noise.fits',
                    array       = a_offcenter_noise,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'offcenter_ROI_5_distances.fits',
                    array       = a_offcenter_distances,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'offcenter_ROI_6_FSRs.fits',
                    array       = a_offcenter_FSRs,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'offcenter_ROI_7_unwrapped_phase_map.fits',
                    array       = a_offcenter_unwrapped,
                    file_format = 'fits' )    

    o_rings_file = tuna.io.read ( file_name = 'rings_ROI_1_raw.fits' )
    a_rings_raw = o_rings_file.get_array ( )
    o_high_res = tuna.tools.phase_map.high_resolution ( array = a_rings_raw,
                                                        bad_neighbours_threshold = 7, 
                                                        channel_threshold = 1, 
                                                        noise_mask_radius = 7,
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )

    a_rings_continuum = o_high_res.get_continuum_array ( )
    a_rings_wrapped   = o_high_res.get_wrapped_phase_map_array ( )
    a_rings_noise     = o_high_res.get_binary_noise_array ( )
    a_rings_distances = o_high_res.get_borders_to_center_distances ( )
    a_rings_FSRs      = o_high_res.get_order_array ( )
    a_rings_unwrapped = o_high_res.get_unwrapped_phase_map_array ( )

    tuna.io.write ( file_name   = 'rings_ROI_2_continuum.fits',
                    array       = a_rings_continuum,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'rings_ROI_3_wrapped_phase_map_barycenter.fits',
                    array       = a_rings_wrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'rings_ROI_4_noise.fits',
                    array       = a_rings_noise,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'rings_ROI_5_distances.fits',
                    array       = a_rings_distances,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'rings_ROI_6_FSRss.fits',
                    array       = a_rings_FSRs,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'rings_ROI_7_unwrapped_phase_map.fits',
                    array       = a_rings_unwrapped,
                    file_format = 'fits' )    

create_ROI_examples ( )
process_ROI_examples ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
