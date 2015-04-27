#!/bin/env ipython3

import numpy
import tuna

raw = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
continuum = tuna.tools.phase_map.detect_continuum ( array = raw.array )
discontinuum = raw - continuum
wrapped = tuna.tools.phase_map.detect_barycenters ( array = discontinuum.array )
center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( wrapped = wrapped )

airy = tuna.tools.models.fit_airy ( beam = 450,
                                    center = center,
                                    finesse = 15.,
                                    focal_length = 0.1,
                                    gap = 1904,
                                    discontinuum = discontinuum )

suppressed = tuna.tools.phase_map.suppress_channel ( array = raw.array, 
                                                     replacement = airy,
                                                     channels = [ 5, 30, 35 ] )

tuna.io.write ( file_name   = 'G094.AD3_channel_suppressed_00_raw.fits',
                array       = raw.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'G094.AD3_channel_suppressed_01_continuum.fits',
                array       = continuum.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'G094.AD3_channel_suppressed_02_discontinuum.fits',
                array       = discontinuum.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'G094.AD3_channel_suppressed_03_airy.fits',
                array       = airy.array,
                file_format = 'fits' )    
tuna.io.write ( file_name   = 'G094.AD3_channel_suppressed_04_suppressed.fits',
                array       = suppressed,
                file_format = 'fits' )    
