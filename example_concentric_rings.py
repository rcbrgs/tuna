#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def g092_find_center ( ):
    g092 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G092/G092.AD3' )
    g092_array = g092.get_array ( )
    g092_ring_center = tuna.tools.phase_map_creation.find_image_center_by_symmetry ( ia_array = g092_array )
    print ( g092_ring_center.get_center ( ) )

g092_find_center ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
