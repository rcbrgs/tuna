#!/bin/env python3

import numpy
import tuna

can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3' )
raw = can.array

center_ROI    = numpy.ndarray ( shape = ( raw.shape[0], 100, 100 ) )
offcenter_ROI = numpy.ndarray ( shape = ( raw.shape[0], 100, 100 ) )
rings_ROI     = numpy.ndarray ( shape = ( raw.shape[0], 400, 400 ) )

for row in range ( 100 ):
    for col in range ( 100 ):
        for dep in range ( a_raw.shape [ 0 ] ):
            center_ROI    [ dep ] [ row ] [ col ] = raw [ dep ] [ row + 170 ] [ col + 200 ]
            offcenter_ROI [ dep ] [ row ] [ col ] = raw [ dep ] [ row + 100 ] [ col + 100 ]

for row in range ( 400 ):
    for col in range ( 400 ):
        for dep in range ( raw.shape [ 0 ] ):
            rings_ROI [ dep ] [ row ] [ col ] = raw [ dep ] [ row ] [ col ]

tuna.io.write ( file_name   = 'center_ROI_1_raw.fits',
                array       = center_ROI, 
                metadata    = [],
                file_format = 'fits' )
tuna.io.write ( file_name   = 'offcenter_ROI_1_raw.fits',
                array       = offcenter_ROI, 
                metadata    = [],
                file_format = 'fits' )
tuna.io.write ( file_name   = 'rings_ROI_1_raw.fits',
                array       = rings_ROI, 
                metadata    = [],
                file_format = 'fits' )

center_ROI_file = tuna.io.read ( file_name = 'center_ROI_1_raw.fits' )
center_ROI_raw = center_ROI_file.array
high_res = tuna.tools.phase_map.high_resolution ( array = center_ROI_raw,
                                                  bad_neighbours_threshold = 7, 
                                                  channel_threshold = 1, 
                                                  noise_mask_radius = 7,
                                                  wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )
center_ROI_continuum = high_res.get_continuum_array ( )
center_ROI_wrapped   = high_res.get_wrapped_phase_map_array ( )
center_ROI_noise     = high_res.get_binary_noise_array ( )
center_ROI_distances = high_res.get_borders_to_center_distances ( )
center_ROI_FSRs      = high_res.get_order_array ( )
center_ROI_unwrapped = high_res.get_unwrapped_phase_map_array ( )

tuna.io.write ( file_name   = 'center_ROI_2_continuum.fits',
                array       = center_ROI_continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_3_wrapped_phase_map_barycenter.fits',
                array       = center_ROI_wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_4_binary_noise.fits',
                array       = center_ROI_noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_5_ring_borders.fits',
                array       = center_ROI_distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_6_orders.fits',
                array       = center_ROI_FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_7_unwrapped_phase_map.fits',
                array       = center_ROI_unwrapped,
                file_format = 'fits' )    

offcenter_file = tuna.io.read ( file_name = 'offcenter_ROI_1_raw.fits' )
offcenter_raw = offcenter_file.array
high_res = tuna.tools.phase_map.high_resolution ( array = offcenter_raw,
                                                  bad_neighbours_threshold = 7, 
                                                  channel_threshold = 1, 
                                                  noise_mask_radius = 7, 
                                                  wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )

offcenter_continuum = high_res.get_continuum_array ( )
offcenter_wrapped   = high_res.get_wrapped_phase_map_array ( )
offcenter_noise     = high_res.get_binary_noise_array ( )
offcenter_distances = high_res.get_borders_to_center_distances ( )
offcenter_FSRs      = high_res.get_order_array ( )
offcenter_unwrapped = high_res.get_unwrapped_phase_map_array ( )

tuna.io.write ( file_name   = 'offcenter_ROI_2_continuum.fits',
                array       = offcenter_continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_3_wrapped_phase_map_barycenter.fits',
                array       = offcenter_wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_4_noise.fits',
                array       = offcenter_noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_5_distances.fits',
                array       = offcenter_distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_6_FSRs.fits',
                array       = offcenter_FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_7_unwrapped_phase_map.fits',
                array       = offcenter_unwrapped,
                file_format = 'fits' )    

rings_file = tuna.io.read ( file_name = 'rings_ROI_1_raw.fits' )
rings_raw = rings_file.array
high_res = tuna.tools.phase_map.high_resolution ( array = a_rings_raw,
                                                  bad_neighbours_threshold = 7, 
                                                  channel_threshold = 1, 
                                                  noise_mask_radius = 7,
                                                  wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array )

rings_continuum = high_res.get_continuum_array ( )
rings_wrapped   = high_res.get_wrapped_phase_map_array ( )
rings_noise     = high_res.get_binary_noise_array ( )
rings_distances = high_res.get_borders_to_center_distances ( )
rings_FSRs      = high_res.get_order_array ( )
rings_unwrapped = high_res.get_unwrapped_phase_map_array ( )

tuna.io.write ( file_name   = 'rings_ROI_2_continuum.fits',
                array       = rings_continuum,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_3_wrapped_phase_map_barycenter.fits',
                array       = rings_wrapped,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_4_noise.fits',
                array       = rings_noise,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_5_distances.fits',
                array       = rings_distances,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_6_FSRss.fits',
                array       = rings_FSRs,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_7_unwrapped_phase_map.fits',
                array       = rings_unwrapped,
                file_format = 'fits' )    
