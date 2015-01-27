#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def g092_create_barycenter ( ):
    g092_raw_file = tuna.io.read ( file_name = 'examples/G092.AD3' )
    g092_barycenter_array = tuna.tools.phase_map_creation.create_barycenter_array ( array = g092_raw_file.get_array ( ) )
    tuna.io.write ( file_name   = 'g092_barycenter.fits',
	            array       = g092_barycenter_array,
                    file_format = 'fits' )

def g092_compare_barycenter ( ):
    g092_barycenter_file = tuna.io.read ( file_name = 'g092_barycenter.fits' )
    g092_barycenter_array = g092_barycenter_file.get_array ( )
    g092_barycenter_gold_file = tuna.io.read ( file_name = 'examples/cal_bru.ad2' )
    g092_barycenter_gold_array = g092_barycenter_gold_file.get_array ( )
    import numpy
    comparison = numpy.ndarray ( shape = g092_barycenter_array.shape )
    for row in range ( comparison.shape[0] ):
        for col in range ( comparison.shape[1] ):
            comparison[row][col] = g092_barycenter_gold_array[comparison.shape[0] - 1 - row][col] - g092_barycenter_array[row][col]

    tuna.io.write ( file_name   = 'g092_barycenter_comparison.fits',
                    array       = comparison,
                    file_format = 'fits' )
    
def g093 ( ):

    g093 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G093/G093.ADT' )
    tuna.io.write ( file_name   = 'g093_fits_file.fits',#
	            array       = g093.get_array    ( ), 
		    metadata    = g093.get_metadata ( ),
		    file_format = 'fits' )
    #g093 = tuna.io.read ( file_name = ( 'g093_fits_file.fits' ) )
    print ( g093.get_metadata ( ) [ 'Acquisition 334 whitelevel'] )

def g094 ( ):

    g094_file = tuna.io.read ( file_name = 'examples/G094.AD3' )
    g094_barycenter_array = tuna.tools.phase_map_creation.create_barycenter_array ( array = g094_file.get_array ( ) )
    tuna.io.write ( file_name   = 'g094_1_phase_brute.fits',
	            array       = g094_barycenter_array,
                    file_format = 'fits' )

#    g094_binary_noise_map = tuna.tools.phase_map_creation.create_binary_noise_array ( array = g094_barycenter_array, bad_neighbours_threshold = 6, channel_threshold = 0.5 )
    g094_binary_noise_map = tuna.tools.phase_map_creation.create_binary_noise_array ( array = g094_barycenter_array )
    tuna.io.write (  file_name   = 'g094_2_binary_noise_map.fits',
	             array       = g094_binary_noise_map,
		     file_format = 'fits' )

    g094_ring_borders_map = tuna.tools.phase_map_creation.create_ring_borders_map ( array = g094_barycenter_array, noise_array = g094_binary_noise_map )
    tuna.io.write (  file_name   = 'g094_3_ring_borders_map.fits',
	             array       = g094_ring_borders_map,
		     file_format = 'fits' )

def airy ( ):

    airy_array = tuna.tools.models.create_airy_array ( )
    tuna.io.write (  file_name   = 'airy.fits',
	             array       = airy_array,
		     file_format = 'fits' )
    
g092_create_barycenter ( )
g092_compare_barycenter ( )
#g093 ( )
#g094 ( )
#airy ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
