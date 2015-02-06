#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def g092_create_ROI_examples ( ):

    g092 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G092/G092.AD3' )
    g092_array = g092.get_array ( )

    import numpy
    central_region_ROI_array = numpy.ndarray ( shape = ( g092_array.shape[0], 100, 100 ) )
    off_center_ROI_array     = numpy.ndarray ( shape = ( g092_array.shape[0], 100, 100 ) )
    second_ring_ROI_array    = numpy.ndarray ( shape = ( g092_array.shape[0], 70, 70 ) )

    for row in range ( 100 ):
        for col in range ( 100 ):
            for dep in range ( g092_array.shape[0] ):
                central_region_ROI_array[dep][row][col] = g092_array[dep][row + 170][col + 200]
                off_center_ROI_array[dep][row][col] = g092_array[dep][row + 100][col + 100]
                if ( row < 70 and
                     col < 70 ):
                    second_ring_ROI_array[dep][row][col] = g092_array[dep][row][col]

    tuna.io.write ( file_name   = 'g092_central_region_1_ROI.fits',
	            array       = central_region_ROI_array, 
		    metadata    = [],
		    file_format = 'fits' )
    tuna.io.write ( file_name   = 'g092_off_center_1_ROI.fits',
	            array       = off_center_ROI_array, 
		    metadata    = [],
		    file_format = 'fits' )
    tuna.io.write ( file_name   = 'g092_second_ring_1_ROI.fits',
	            array       = second_ring_ROI_array, 
		    metadata    = [],
		    file_format = 'fits' )

def g092_process_ROI_examples ( ):
    g092_central_region_raw_file = tuna.io.read ( file_name = 'g092_central_region_1_ROI.fits' )
    g092_central_region_array = g092_central_region_raw_file.get_array ( )
    high_res_FP_phase_map_tool = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( array = g092_central_region_array,wrapped_phase_map_algorithm = tuna.tools.phase_map_creation.create_barycenter_array, channel_threshold = 1, bad_neighbours_threshold = 7, noise_mask_radius = 7 )
    g092_central_region_wrapped_array = high_res_FP_phase_map_tool.get_wrapped_phase_map_array ( )
    g092_central_region_continuum_array = high_res_FP_phase_map_tool.get_continuum_array ( )
    g092_central_region_unwrapped_array = high_res_FP_phase_map_tool.get_unwrapped_phase_map_array ( )
    g092_central_region_binary_noise_array = high_res_FP_phase_map_tool.get_binary_noise_array ( )
    g092_central_region_ring_borders_array = high_res_FP_phase_map_tool.get_ring_borders_array ( )
    g092_central_region_regions_array = high_res_FP_phase_map_tool.get_regions_array ( )
    g092_central_region_order_array = high_res_FP_phase_map_tool.get_order_array ( )

    tuna.io.write ( file_name   = 'g092_central_region_2_continuum.fits',
                    array       = g092_central_region_continuum_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_central_region_3_wrapped_phase_map_barycenter.fits',
                    array       = g092_central_region_wrapped_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_central_region_4_binary_noise.fits',
                    array       = g092_central_region_binary_noise_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_central_region_5_ring_borders.fits',
                    array       = g092_central_region_ring_borders_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_central_region_6_regions.fits',
                    array       = g092_central_region_regions_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_central_region_7_orders.fits',
                    array       = g092_central_region_order_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_central_region_8_unwrapped_phase_map.fits',
                    array       = g092_central_region_unwrapped_array,
                    file_format = 'fits' )    

    g092_off_center_raw_file = tuna.io.read ( file_name = 'g092_off_center_1_ROI.fits' )
    g092_off_center_array = g092_off_center_raw_file.get_array ( )
    high_res_FP_phase_map_tool = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( array = g092_off_center_array,wrapped_phase_map_algorithm = tuna.tools.phase_map_creation.create_barycenter_array, channel_threshold = 1, bad_neighbours_threshold = 7, noise_mask_radius = 7 )
    g092_off_center_wrapped_array = high_res_FP_phase_map_tool.get_wrapped_phase_map_array ( )
    g092_off_center_continuum_array = high_res_FP_phase_map_tool.get_continuum_array ( )
    g092_off_center_unwrapped_array = high_res_FP_phase_map_tool.get_unwrapped_phase_map_array ( )
    g092_off_center_binary_noise_array = high_res_FP_phase_map_tool.get_binary_noise_array ( )
    g092_off_center_ring_borders_array = high_res_FP_phase_map_tool.get_ring_borders_array ( )
    g092_off_center_regions_array = high_res_FP_phase_map_tool.get_regions_array ( )
    g092_off_center_order_array = high_res_FP_phase_map_tool.get_order_array ( )

    tuna.io.write ( file_name   = 'g092_off_center_2_continuum.fits',
                    array       = g092_off_center_continuum_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_off_center_3_wrapped_phase_map_barycenter.fits',
                    array       = g092_off_center_wrapped_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_off_center_4_binary_noise.fits',
                    array       = g092_off_center_binary_noise_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_off_center_5_ring_borders.fits',
                    array       = g092_off_center_ring_borders_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_off_center_6_regions.fits',
                    array       = g092_off_center_regions_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_off_center_7_orders.fits',
                    array       = g092_off_center_order_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_off_center_8_unwrapped_phase_map.fits',
                    array       = g092_off_center_unwrapped_array,
                    file_format = 'fits' )    

    g092_second_ring_raw_file = tuna.io.read ( file_name = 'g092_second_ring_1_ROI.fits' )
    g092_second_ring_array = g092_second_ring_raw_file.get_array ( )
    high_res_FP_phase_map_tool = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( array = g092_second_ring_array,wrapped_phase_map_algorithm = tuna.tools.phase_map_creation.create_barycenter_array, channel_threshold = 1, bad_neighbours_threshold = 7, noise_mask_radius = 7 )
    g092_second_ring_wrapped_array = high_res_FP_phase_map_tool.get_wrapped_phase_map_array ( )
    g092_second_ring_continuum_array = high_res_FP_phase_map_tool.get_continuum_array ( )
    g092_second_ring_unwrapped_array = high_res_FP_phase_map_tool.get_unwrapped_phase_map_array ( )
    g092_second_ring_binary_noise_array = high_res_FP_phase_map_tool.get_binary_noise_array ( )
    g092_second_ring_ring_borders_array = high_res_FP_phase_map_tool.get_ring_borders_array ( )
    g092_second_ring_regions_array = high_res_FP_phase_map_tool.get_regions_array ( )
    g092_second_ring_order_array = high_res_FP_phase_map_tool.get_order_array ( )

    tuna.io.write ( file_name   = 'g092_second_ring_2_continuum.fits',
                    array       = g092_second_ring_continuum_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_second_ring_3_wrapped_phase_map_barycenter.fits',
                    array       = g092_second_ring_wrapped_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_second_ring_4_binary_noise.fits',
                    array       = g092_second_ring_binary_noise_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_second_ring_5_ring_borders.fits',
                    array       = g092_second_ring_ring_borders_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_second_ring_6_regions.fits',
                    array       = g092_second_ring_regions_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_second_ring_7_orders.fits',
                    array       = g092_second_ring_order_array,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = 'g092_second_ring_8_unwrapped_phase_map.fits',
                    array       = g092_second_ring_unwrapped_array,
                    file_format = 'fits' )    

g092_create_ROI_examples ( )
g092_process_ROI_examples ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
