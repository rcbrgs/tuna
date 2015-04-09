#!/bin/env ipython3

import numpy
import tuna

compare_one = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/compare_one.fits' )
compare_two = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/compare_two.fits' )

comparison = compare_one.array - compare_two.array
tuna.io.write ( file_name   = 'comparison.fits',
                array       = comparison,
                file_format = 'fits' )
