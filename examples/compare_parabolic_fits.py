#!/bin/env ipython3

import numpy
import tuna

o_compever_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_compever_prb.ad2' )
a_compever      = o_compever_file.array
o_ADHOC_file    = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_adhoc_prb.fits' )
a_adhoc         = o_ADHOC_file.array

a_comparison = a_compever - a_adhoc
tuna.io.write ( file_name   = 'G094.AD3_ADHOC_computeeverything_parabolic_fit_comparison.fits',
                array       = a_comparison,
                file_format = 'fits' )

o_tuna_file     = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3_08_parabolic_model.fits' )
a_tuna          = o_tuna_file.array

a_comparison = a_compever - a_tuna
tuna.io.write ( file_name   = 'G094.AD3_computeverything_Tuna_parabolic_fit_comparison.fits',
                array       = a_comparison,
                file_format = 'fits' )

a_comparison = a_adhoc - a_tuna
tuna.io.write ( file_name   = 'G094.AD3_ADHOC_Tuna_parabolic_fit_comparison.fits',
                array       = a_comparison,
                file_format = 'fits' )
