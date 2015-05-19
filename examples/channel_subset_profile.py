#!/bin/env ipython3

import numpy
import random
import tuna

tuna.log.set_path ( "channel_subset_profile.log" )

raw = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
continuum = tuna.tools.phase_map.detect_continuum ( array = raw.array )
discontinuum = raw.array - continuum.array
discontinuum_can = tuna.io.can ( array = discontinuum )
wrapped = tuna.tools.phase_map.detect_barycenters ( array = discontinuum_can.array )
center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( wrapped = wrapped )

airy = tuna.tools.models.fit_airy ( beam = 450,
                                    center = center,
                                    finesse = 15.,
                                    focal_length = 0.1,
                                    gap = 0.1,
                                    initial_gap = 1904,
                                    discontinuum = discontinuum_can,
                                    pixel_size = 9 )

def generate_data ( channels ):
    print ( "sleeping a little so you can cancel the run." )
    import time
    time.sleep ( 5 )
    print ( "starting with %d channels suppressed." % len ( channels ) )

    suppressed = tuna.tools.phase_map.suppress_channel ( array = raw.array, 
                                                         replacement = airy,
                                                         channels = channels )
    suppressed_can = tuna.io.can ( array = suppressed )
    
    channel_string = ""
    for channel in channels:
        channel_string += str ( channel ) + "_"

    high_res = tuna.tools.phase_map.high_resolution ( tuna_can = suppressed_can,
                                                      beam = 450,
                                                      calibration_wavelength = 6598.950,
                                                      finesse = 15.,
                                                      focal_length = 0.1,
                                                      free_spectral_range = 8.36522123894,
                                                      gap = 0.01,
                                                      initial_gap = 1904,
                                                      interference_order = 798,
                                                      interference_reference_wavelength = 6562.7797852,
                                                      pixel_size = 9,
                                                      channel_threshold = 1, 
                                                      bad_neighbours_threshold = 7, 
                                                      noise_mask_radius = 7,
                                                      scanning_wavelength = 6616.895 )

    unwrapped   = high_res.get_unwrapped_phase_map_array ( )
    compare_one = unwrapped
    compare_two = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_07_unwrapped.fits' )
    comparison  = compare_one - compare_two.array

    return numpy.sum ( numpy.square ( comparison ) ) # divide by num pixels

number_of_pixels = raw.array.shape [ 0 ] * raw.array.shape [ 1 ] * raw.array.shape [ 2 ]
tabular_data = [ ]
repetitions = 50

for c in range ( 1, 35 ):
    subset_sum = 0
    subset_values = [ ]
    for t in range ( repetitions ):
        random_channel_list = [ ]
        while ( len ( random_channel_list ) < c ):
            some_channel = random.randint ( 0, 35 )
            if ( some_channel not in random_channel_list ):
                random_channel_list.append ( some_channel )
        print ( "random_channel_list = %s" % str ( random_channel_list ) )           
        data = generate_data ( random_channel_list ) / number_of_pixels
        subset_sum += data
        subset_values.append ( data )

    tabular_data.append ( ( c, subset_sum / repetitions, subset_values ) )
    for entry in tabular_data:
        print ( "%s, %s, %s" % ( entry [ 0 ], entry [ 1 ], entry [ 2 ] ) )
