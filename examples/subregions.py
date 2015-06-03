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
        for dep in range ( raw.shape [ 0 ] ):
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
high_res = tuna.tools.phase_map.high_resolution ( beam = 450,
                                                  calibration_wavelength = 6598.950,
                                                  finesse = 15.,
                                                  focal_length = 0.1,
                                                  free_spectral_range = 8.36522123894,
                                                  gap = 1904,
                                                  interference_order = 798,
                                                  interference_reference_wavelength = 6562.7797852,
                                                  tuna_can = center_ROI_file,
                                                  noise_mask_radius = 1,
                                                  scanning_wavelength = 6616.895 )

high_res.start ( )
high_res.join ( )

center_ROI_continuum = high_res.continuum
center_ROI_wrapped   = high_res.wrapped_phase_map
center_ROI_noise     = high_res.noise
center_ROI_distances = high_res.borders_to_center_distances
center_ROI_FSRs      = high_res.order_map
center_ROI_unwrapped = high_res.unwrapped_phase_map

tuna.io.write ( file_name   = 'center_ROI_2_continuum.fits',
                array       = center_ROI_continuum.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_3_wrapped_phase_map_barycenter.fits',
                array       = center_ROI_wrapped.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_4_binary_noise.fits',
                array       = center_ROI_noise.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_5_ring_borders.fits',
                array       = center_ROI_distances.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_6_orders.fits',
                array       = center_ROI_FSRs.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'center_ROI_7_unwrapped_phase_map.fits',
                array       = center_ROI_unwrapped.array,
                file_format = 'fits' )    

offcenter_file = tuna.io.read ( file_name = 'offcenter_ROI_1_raw.fits' )
high_res = tuna.tools.phase_map.high_resolution ( beam = 450,
                                                  calibration_wavelength = 6598.950,
                                                  finesse = 15.,
                                                  focal_length = 0.1,
                                                  free_spectral_range = 8.36522123894,
                                                  gap = 1904,
                                                  interference_order = 798,
                                                  interference_reference_wavelength = 6562.7797852,
                                                  tuna_can = offcenter_file,
                                                  noise_mask_radius = 1,
                                                  scanning_wavelength = 6616.895 )
high_res.start ( )
high_res.join ( )

offcenter_continuum = high_res.continuum
offcenter_wrapped   = high_res.wrapped_phase_map
offcenter_noise     = high_res.noise
offcenter_distances = high_res.borders_to_center_distances
offcenter_FSRs      = high_res.order_map
offcenter_unwrapped = high_res.unwrapped_phase_map

tuna.io.write ( file_name   = 'offcenter_ROI_2_continuum.fits',
                array       = offcenter_continuum.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_3_wrapped_phase_map_barycenter.fits',
                array       = offcenter_wrapped.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_4_noise.fits',
                array       = offcenter_noise.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_5_distances.fits',
                array       = offcenter_distances.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_6_FSRs.fits',
                array       = offcenter_FSRs.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'offcenter_ROI_7_unwrapped_phase_map.fits',
                array       = offcenter_unwrapped.array,
                file_format = 'fits' )    

rings_file = tuna.io.read ( file_name = 'rings_ROI_1_raw.fits' )
high_res = tuna.tools.phase_map.high_resolution ( beam = 450,
                                                  calibration_wavelength = 6598.950,
                                                  finesse = 15.,
                                                  focal_length = 0.1,
                                                  free_spectral_range = 8.36522123894,
                                                  gap = 1904,
                                                  interference_order = 798,
                                                  interference_reference_wavelength = 6562.7797852,
                                                  tuna_can = rings_file,
                                                  noise_mask_radius = 1,
                                                  scanning_wavelength = 6616.895 )
high_res.start ( )
high_res.join ( )


rings_continuum = high_res.continuum
rings_wrapped   = high_res.wrapped_phase_map
rings_noise     = high_res.noise
rings_distances = high_res.borders_to_center_distances
rings_FSRs      = high_res.order_map
rings_unwrapped = high_res.unwrapped_phase_map

tuna.io.write ( file_name   = 'rings_ROI_2_continuum.fits',
                array       = rings_continuum.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_3_wrapped_phase_map_barycenter.fits',
                array       = rings_wrapped.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_4_noise.fits',
                array       = rings_noise.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_5_distances.fits',
                array       = rings_distances.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_6_FSRss.fits',
                array       = rings_FSRs.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'rings_ROI_7_unwrapped_phase_map.fits',
                array       = rings_unwrapped.array,
                file_format = 'fits' )    
