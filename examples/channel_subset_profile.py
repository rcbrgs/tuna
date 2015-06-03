#!/bin/env ipython3

import math
import numpy
import random
import tuna

tuna.log.set_path ( "channel_subset_profile.log" )

raw      = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
airy     = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_09_airy_fit.fits' )
comparee = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_07_unwrapped.fits' )  

error_threshold = 0.1
true_center = ( 219, 259 )
center_difference_threshold = 11

def generate_data ( channels ):
    suppressed = tuna.tools.phase_map.suppress_channel ( array = raw.array, 
                                                         replacement = airy,
                                                         channels = channels )
    suppressed_can = tuna.io.can ( array = suppressed )
    
    channel_string = "G094.AD3-channel_substituted-"
    channel_string += str ( len ( channels ) )
    for channel in sorted ( channels ):
        channel_string += "_" + str ( channel )

    tuna.io.write ( suppressed_can.array, 'fits', channel_string + "_1-raw.fits" )
        
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
                                                          noise_mask_radius = 1,
                                                          scanning_wavelength = 6616.895,
                                                          dont_fit = True,
                                                          unwrapped_only = True,
                                                          verify_center = ( true_center, center_difference_threshold ) )

        high_res.start ( )
        high_res.join ( )

        center = high_res.rings_center
        difference = math.sqrt ( ( center [ 0 ] - true_center [ 0 ] ) ** 2 + \
                                 ( center [ 1 ] - true_center [ 1 ] ) ** 2 )
        print ( "center = %s, difference = %f" % ( str ( center ), difference ) )

        tuna.io.write ( high_res.continuum.array, 'fits', channel_string + "-2_continuum.fits" )
        tuna.io.write ( high_res.discontinuum.array, 'fits', channel_string + "-3_discontinuum.fits" )
        tuna.io.write ( high_res.wrapped_phase_map.array, 'fits', channel_string + "-4_wrapped.fits" )
        tuna.io.write ( high_res.noise.array, 'fits', channel_string + "-5_noise.fits" )
        
    if difference < center_difference_threshold:

        unwrapped = high_res.unwrapped_phase_map
        tuna.io.write ( high_res.order_map.array, 'fits', channel_string + "-6_order.fits" )
        tuna.io.write ( unwrapped.array, 'fits', channel_string + "-7_unwrapped.fits" )

        try:
            comparison = unwrapped.array - comparee.array
        except:
            print ( "exception during diff" )
            return None

        return numpy.sum ( numpy.abs ( comparison ) )

    else:
        return None    

number_of_pixels = raw.array.shape [ 0 ] * raw.array.shape [ 1 ] * raw.array.shape [ 2 ]
tabular_data = [ ]
repetitions = 10

for c in range ( 6, 35 ):
    print ( "Beginning to produce %d channels suppressed data." % c )
    filtered_max = 0.0
    filtered_min = 2.0
    subset_sum = 0
    subset_values = [ ]

    for t in range ( 1, repetitions + 1 ):
        print ( "repetition %d" % t )
        error = error_threshold
        while ( error >= error_threshold ):
            data = None
            while ( data == None ):
                random_channel_list = [ ]
                while ( len ( random_channel_list ) < c ):
                    some_channel = random.randint ( 0, 35 )
                    if ( some_channel not in random_channel_list ):
                        random_channel_list.append ( some_channel )
                print ( "%s: " % str ( sorted ( random_channel_list ) ) )
                data = generate_data ( random_channel_list )
                print ( "data = %s" % str ( data ) )

            error = data / number_of_pixels
            print ( "data / number_of_pixels = %f" % ( error ) )
            
        print ( "(%d) error = %f" % ( t, error ) )
        subset_sum += error
        filtered_max = max ( error, filtered_max )
        filtered_min = min ( error, filtered_min )
        subset_values.append ( ( random_channel_list, data, error ) )

    tabular_data.append ( ( c, 
                            subset_sum / repetitions,
                            filtered_max - filtered_min,
                            subset_values ) )

    print ( "# suppressed, filtered_avg, err_estimate" )
    for entry in tabular_data:
        print ( "%d, %f, %f" % ( entry [ 0 ], entry [ 1 ], entry [ 2 ] ) )

for entry in tabular_data:
    print ( "%d, %f, %f, %s" % ( entry [ 0 ], entry [ 1 ], entry [ 2 ], str ( entry [ 3 ] ) ) )
