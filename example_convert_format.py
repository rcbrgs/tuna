#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def g092_convert_file ( ):

    g092 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G092/G092.AD3' )
    g092_array = g092.get_array ( )

    tuna.io.write ( file_name   = 'g092_raw.fits',
                    array       = g092_array, 
                    metadata    = g092.get_metadata ( ),
                    file_format = 'fits' )

g092_convert_file ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
