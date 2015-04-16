#!/bin/env ipython3

import numpy
import tuna

compare_one = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_07_unwrapped.fits' )
compare_two = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_compever_prb.ad2' )

comparison = compare_one.array - compare_two.array
tuna.io.write ( file_name   = 'comparison.fits',
                array       = comparison,
                file_format = 'fits' )
