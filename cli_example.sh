#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here. For example, let's open an ADHOC file and calculate its phase map:
some_adhoc_file = tuna.file_format.adhoc ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G094/G094.AD3' )
phase_map = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_object = some_adhoc_file )
# now let's create a fits object from the phase map object and save it as a fits file:
new_fits_object = tuna.file_format.fits ( image_ndarray = phase_map.get_image_ndarray ( ) )
new_fits_object.write ( file_name = '/home/nix/phase_map.fits' )

# Calling the GUI doesn't return yet, but is useful for tests so here it is an example:
#tuna.gui.window_2d_viewer ( ndarray_object = new_fits_object.get_image_ndarray ( ) )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
