#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_compever_bru.ad2' )
raw = can.array

tuna.io.write ( file_name   = 'g092_compever_bru.fits',
                array       = raw, 
                metadata    = can.metadata,
                file_format = 'fits' )
