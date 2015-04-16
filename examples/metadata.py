#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G093/G093.ADT' )
tuna.io.write ( file_name   = 'g093.fits',
                array       = can.array, 
                metadata    = can.metadata,
                file_format = 'fits' )
can_fits = tuna.io.read ( file_name = ( 'g093.fits' ) )
print ( can_fits.metadata )
print ( can_fits.metadata [ 'QUEENSG' ] )
