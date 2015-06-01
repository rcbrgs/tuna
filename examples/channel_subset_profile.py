#!/bin/env ipython3

import numpy
import random
import tuna

tuna.log.set_path ( "channel_subset_profile.log" )

raw      = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
airy     = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_09_airy_fit.fits' )
comparee = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_07_unwrapped.fits' )  

true_center = ( 219, 259 )
center_difference_threshold = 6

def generate_data ( channels ):
    suppressed = tuna.tools.phase_map.suppress_channel ( array = raw.array, 
                                                         replacement = airy,
                                                         channels = channels )
    suppressed_can = tuna.io.can ( array = suppressed )
    
    channel_string = "G094.AD3-channel_substituted-"
    channel_string += str ( len ( channels ) )
    for channel in channels:
        channel_string += "_" + str ( channel )
    channel_string += ".fits"

    difference = 100
    attempts = 0

    while ( difference > center_difference_threshold ):
        attempts += 1
        if attempts > 3:
            return None
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
                                                          scanning_wavelength = 6616.895,
                                                          dont_fit = True )

        high_res.start ( )
        high_res.join ( )

        center = high_res.rings_center
        difference = abs ( center [ 0 ] - true_center [ 0 ] ) + \
                     abs ( center [ 1 ] - true_center [ 1 ] )
        print ( "center = %s, difference = %d" % ( str ( center ), difference ) )
    
    unwrapped = high_res.unwrapped_phase_map
    tuna.io.write ( unwrapped.array, 'fits', channel_string )

    try:
        comparison = unwrapped.array - comparee.array
    except:
        print ( "exception during diff" )
        return None

    return numpy.sum ( numpy.abs ( comparison ) ) 

number_of_pixels = raw.array.shape [ 0 ] * raw.array.shape [ 1 ] * raw.array.shape [ 2 ]
tabular_data = [ ]
repetitions = 10
error_threshold = 2.0

for c in range ( 21, 35 ):
    print ( "Beginning to produce %d channels suppressed data." % c )
    filtered_max = 0.0
    filtered_min = 2.0
    filtered_sum = 0
    filtered_count = 0
    subset_sum = 0
    subset_values = [ ]
    for t in range ( repetitions ):
        random_channel_list = [ ]
        while ( len ( random_channel_list ) < c ):
            some_channel = random.randint ( 0, 35 )
            if ( some_channel not in random_channel_list ):
                random_channel_list.append ( some_channel )
        print ( "%s: " % str ( random_channel_list ) )
        data = generate_data ( random_channel_list )
        #print ( "data generated" )
        if data == None:
            #print ( "random_channel_list = %s, error = None" % ( str ( random_channel_list ) ) )
            print ( "invalid data" )
            continue

        data /= number_of_pixels
        print ( "error = %f" % ( data ) )
        subset_sum += data
        if data < error_threshold:
            filtered_sum += data
            filtered_count += 1
            filtered_max = max ( data, filtered_max )
            filtered_min = min ( data, filtered_min )
        subset_values.append ( ( random_channel_list, data ) )

    tabular_data.append ( ( c, 
                            subset_sum / len ( subset_values ), 
                            filtered_sum / filtered_count,
                            filtered_max - filtered_min,
                            subset_values ) )

    print ( "# suppressed, filtered_avg, err_estimate" )
    for entry in tabular_data:
        print ( "%s, %f, %f" % ( entry [ 0 ], entry [ 2 ], entry [ 3 ] ) )

for entry in tabular_data:
    print ( "%d, %f, %f, %f, %s" % ( entry [ 0 ], entry [ 1 ], entry [ 2 ], entry [ 3 ], str ( entry [ 4 ] ) ) )
