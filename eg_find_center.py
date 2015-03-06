#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

def find_center_by_symmetry ( ):
    o_file = tuna.io.read ( file_name = 'sample_data/G092.AD3' )
    a_raw  = o_file.get_array ( )
    t_ring_center = tuna.tools.phase_map.find_image_center_by_symmetry ( ia_data = a_raw )
    print ( "Center found by symmetry: %s" % str ( t_ring_center ) )

def find_center_by_arcs ( ):
    o_file = tuna.io.read ( file_name = 'sample_data/G092.AD3' )
    a_raw  = o_file.get_array ( )
    a_barycenter = tuna.tools.phase_map.create_barycenter_array ( array = a_raw )
    t_ring_center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( ffa_unwrapped = a_barycenter )
    print ( "Center found by arc segmentation: %s" % str ( t_ring_center ) )

find_center_by_symmetry ( )
find_center_by_arcs ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )
