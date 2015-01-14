#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def g092 ( ):
    g092 = tuna.file_format.adhoc ( file_name = 'examples/G092.AD3' )
    g092_phase_map = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_object = g092 )

    fits_object = tuna.file_format.fits ( image_ndarray = g092_phase_map.get_max_channel_map ( ) )
    fits_object.write ( file_name = 'g092_1_max_channel_map.fits' )

    fits_object = tuna.file_format.fits ( image_ndarray = g092_phase_map.get_binary_noise_map ( ) )
    fits_object.write ( file_name = 'g092_2_binary_noise_map.fits' )

    fits_object = tuna.file_format.fits ( image_ndarray = g092_phase_map.get_ring_borders_map ( ) )
    fits_object.write ( file_name = 'g092_3_ring_borders_map.fits' )

    fits_object = tuna.file_format.fits ( image_ndarray = g092_phase_map.get_regions_map ( ) )
    fits_object.write ( file_name = 'g092_4_regions_map.fits' )

    fits_object = tuna.file_format.fits ( image_ndarray = g092_phase_map.get_order_map ( ) )
    fits_object.write ( file_name = 'g092_5_order_map.fits' )

    fits_object = tuna.file_format.fits ( image_ndarray = g092_phase_map.get_unwrapped_phases_map ( ) )
    fits_object.write ( file_name = 'g092_6_unwrapped_phases_map.fits' )

def g094 ( ):
    g094_image = tuna.file_format.ada ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G093/G093.ADT' )
    fits_object = tuna.file_format.fits ( image_ndarray = g094_image.get_image_ndarray ( ) )
    fits_object.write ( file_name = 'g094_0_photon_counts.fits' )

g092 ( )
#g094 ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
