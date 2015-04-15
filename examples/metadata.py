#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G093/G093.ADT' )
tuna.io.write ( file_name   = 'g093.fits',
                array       = o_file.get_array ( ), 
                metadata    = o_file.get_metadata ( ),
                file_format = 'fits' )
o_file_fits = tuna.io.read ( file_name = ( 'g093.fits' ) )
print ( o_file_fits.get_metadata_parameter ( parameter = 'EXPOSUR' ) )
