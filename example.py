#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def g092_create_ROI_examples ( ):

    g092 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G092/G092.AD3' )
    g092_array = g092.get_array ( )
    import numpy
    central_region_ROI_array = numpy.ndarray ( shape = ( g092_array.shape[0], 100, 100 ) )
    for row in range ( 100 ):
        for col in range ( 100 ):
            for dep in range ( g092_array.shape[0] ):
                central_region_ROI_array[dep][row][col] = g092_array[dep][row + 170][col + 200]

    tuna.io.write ( file_name   = 'g092_central_region_ROI.fits',
	            array       = central_region_ROI_array, 
		    metadata    = [],
		    file_format = 'fits' )

g092_create_ROI_examples ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
