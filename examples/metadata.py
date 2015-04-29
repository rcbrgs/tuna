#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G093/G093.ADT' )
for entry in can.metadata.keys ( ):
    print ( "metadata [ %s ] = %s" % ( entry, 
                                       can.metadata [ entry ] ) )
tuna.io.write ( file_name   = 'g093.fits',
                array       = can.array, 
                metadata    = can.metadata,
                file_format = 'fits' )
can_fits = tuna.io.read ( file_name = ( 'g093.fits' ) )
for entry in can_fits.metadata.keys ( ):
    print ( "metadata [ %s ] = %s" % ( entry, 
                                       can_fits.metadata [ entry ] ) )
