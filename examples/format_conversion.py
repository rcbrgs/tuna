#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/g094_compever_bru.ad2' )
a_raw = o_file.array

tuna.io.write ( file_name   = 'g092_compever_bru.fits',
                array       = a_raw, 
                metadata    = o_file.get_metadata ( ),
                file_format = 'fits' )
