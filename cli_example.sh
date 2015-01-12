#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
g094_image     = tuna.file_format.adhoc ( file_name = 'G094.AD3' )
g094_phase_map = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_object = g094_image )

fits_object = tuna.file_format.fits ( image_ndarray = g094_phase_map.get_max_channel_map ( ) )
fits_object.write ( file_name = 'g094_1_max_channel_map.fits' )

fits_object = tuna.file_format.fits ( image_ndarray = g094_phase_map.get_binary_noise_map ( ) )
fits_object.write ( file_name = 'g094_2_binary_noise_map.fits' )

fits_object = tuna.file_format.fits ( image_ndarray = g094_phase_map.get_ring_borders_map ( ) )
fits_object.write ( file_name = 'g094_3_ring_borders_map.fits' )

fits_object = tuna.file_format.fits ( image_ndarray = g094_phase_map.get_regions_map ( ) )
fits_object.write ( file_name = 'g094_4_regions_map.fits' )

fits_object = tuna.file_format.fits ( image_ndarray = g094_phase_map.get_order_map ( ) )
fits_object.write ( file_name = 'g094_5_order_map.fits' )

fits_object = tuna.file_format.fits ( image_ndarray = g094_phase_map.get_unwrapped_phases_map ( ) )
fits_object.write ( file_name = 'g094_6_unwrapped_phases_map.fits' )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
