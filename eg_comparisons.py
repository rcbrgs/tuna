#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def compare_ADHOC_computeeverything ( ):
    o_compever_file = tuna.io.read ( file_name = 'sample_data/g094_compever_bru.ad2' )
    a_compever      = o_compever_file.get_array ( )
    o_ADHOC_file    = tuna.io.read ( file_name = 'sample_data/g094_adhoc_bru.fits' )
    a_adhoc         = o_ADHOC_file.get_array ( )

    import numpy
    a_comparison = numpy.ndarray ( shape = a_compever.shape )
    for i_row in range ( a_comparison.shape[0] ):
        for i_col in range ( a_comparison.shape[1] ):
            a_comparison [ i_row ] [ i_col ] = ( a_compever [ i_row ] [ i_col ] - 
                                                 a_adhoc    [ i_row ] [ i_col ] )

    tuna.io.write ( file_name   = 'g094_ADHOC_computeverything_wrapped_comparison.fits',
                    array       = a_comparison,
                    file_format = 'fits' )

def compare_tuna_computeeverything ( ):
    o_compever_file = tuna.io.read ( file_name = 'sample_data/g094_compever_bru.ad2' )
    a_compever      = o_compever_file.get_array ( )
    o_tuna_file     = tuna.io.read ( file_name = 'sample_data/g094_tuna_wrapped.fits' )
    a_tuna          = o_tuna_file.get_array ( )

    import numpy
    a_comparison = numpy.ndarray ( shape = a_compever.shape )
    for i_row in range ( a_comparison.shape[0] ):
        for i_col in range ( a_comparison.shape[1] ):
            a_comparison [ i_row ] [ i_col ] = ( a_compever [ i_row ] [ i_col ] - 
                                                 a_tuna     [ i_row ] [ i_col ] )

    tuna.io.write ( file_name   = 'g094_computeverything_tuna_wrapped_comparison.fits',
                    array       = a_comparison,
                    file_format = 'fits' )

def compare_tuna_ADHOC ( ):
    o_ADHOC_file = tuna.io.read ( file_name = 'sample_data/g094_adhoc_bru.fits' )
    a_ADHOC      = o_ADHOC_file.get_array ( )
    o_tuna_file  = tuna.io.read ( file_name = 'sample_data/g094_tuna_wrapped.fits' )
    a_tuna       = o_tuna_file.get_array ( )

    import numpy
    a_comparison = numpy.ndarray ( shape = a_tuna.shape )
    for i_row in range ( a_comparison.shape[0] ):
        for i_col in range ( a_comparison.shape[1] ):
            a_comparison [ i_row ] [ i_col ] = ( a_ADHOC [ i_row ] [ i_col ] - 
                                                 a_tuna  [ i_row ] [ i_col ] )

    tuna.io.write ( file_name   = 'g094_ADHOC_tuna_wrapped_comparison.fits',
                    array       = a_comparison,
                    file_format = 'fits' )

compare_ADHOC_computeeverything ( )    
compare_tuna_computeeverything ( )    
compare_tuna_ADHOC ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
