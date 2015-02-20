#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def g093_metadata ( ):

    g093 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G093/G093.ADT' )
    tuna.io.write ( file_name   = 'g093_fits_file.fits',
	            array       = g093.get_array    ( ), 
		    metadata    = g093.get_metadata ( ),
		    file_format = 'fits' )

g093_metadata ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
