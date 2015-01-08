#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here. For example, let's open an ADHOC file and calculate its phase map:
some_adhoc_file = tuna.file_format.adhoc ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G094/G094.AD3' )
phase_map = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_object = some_adhoc_file )

#phase_map_viewer = tuna.gui.window_2d_viewer ( ndarray_object = phase_map.get_image_ndarray ( ) )

tuna_daemons.finish ( )
