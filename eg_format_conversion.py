#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def convert_file ( ):

    o_file = tuna.io.read ( file_name = 'sample_data/G092.AD3' )
    a_raw = o_file.get_array ( )

    tuna.io.write ( file_name   = 'raw.fits',
                    array       = a_raw, 
                    metadata    = o_file.get_metadata ( ),
                    file_format = 'fits' )

convert_file ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
