#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def g092 ( ):

    g092_file = tuna.io.read ( file_name = 'examples/G092.AD3' )
    g092_barycenter = tuna.tools.phase_map_creation.barycenter ( array = g092_file.get_array ( ) )
    g092_barycenter_array = g092_barycenter.run ( )
   
    tuna.io.write ( file_name   = 'g092_0_photon_counts.fits',
	            array       = g092_barycenter.get_photon_counts_array ( ),
                    file_format = 'fits' )

    tuna.io.write ( file_name   = 'g092_1_number_of_spectral_regions.fits',
	            array       = g092_barycenter.get_number_of_spectral_regions_array ( ),
                    file_format = 'fits' )

    tuna.io.write ( file_name   = 'g092_2_number_of_spectral_peaks.fits',
	            array       = g092_barycenter.get_number_of_spectral_peaks_array ( ),
                    file_format = 'fits' )

    tuna.io.write ( file_name   = 'g092_9_barycenter.fits',
	            array       = g092_barycenter_array,
                    file_format = 'fits' )


#    g092_binary_noise_map = tuna.tools.phase_map_creation.create_binary_noise_array ( array = g092_barycenter_array, bad_neighbours_threshold = 6, channel_threshold = 0.5 )
    #g092_binary_noise_map = tuna.tools.phase_map_creation.create_binary_noise_array ( array = g092_barycenter_array )
    #tuna.io.write (  file_name   = 'g092_2_binary_noise_map.fits',
#	             array       = g092_binary_noise_map,
#		     file_format = 'fits' )
#
#    g092_ring_borders_map = tuna.tools.phase_map_creation.create_ring_borders_map ( array = g092_barycenter_array, noise_array = g092_binary_noise_map )
#    tuna.io.write (  file_name   = 'g092_3_ring_borders_map.fits',
#	             array       = g092_ring_borders_map,
#		     file_format = 'fits' )

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
    
g092 ( )
#g093 ( )
#g094 ( )
#airy ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
