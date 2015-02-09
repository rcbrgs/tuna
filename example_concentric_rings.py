#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def g092_find_rings ( ):

    g092 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G092/G092.AD3' )
    g092_array = g092.get_array ( )

    #import tuna.tools.phase_map.concentric_rings_model.find_concentric_rings_center
    g092_ring_center = tuna.tools.phase_map_creation.find_concentric_rings_center ( ia_array = g092_array )
    print ( g092_ring_center )

    #tuna.io.write ( file_name   = 'g092_central_region_1_ROI.fits',
	#            array       = central_region_ROI_array, 
	#	    metadata    = [],
	#	    file_format = 'fits' )

g092_find_rings ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
