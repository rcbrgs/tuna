#!/bin/env python3

import tuna

# find_center_by_symmetry:
o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3' )
a_raw  = o_file.array
t_ring_center = tuna.tools.phase_map.find_image_center_by_symmetry ( ia_data = a_raw )
print ( "Center found by symmetry: %s" % str ( t_ring_center ) )

# find_center_by_arcs:
o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3' )
a_raw  = o_file.array
a_barycenter = tuna.tools.phase_map.create_barycenter_array ( array = a_raw )
t_ring_center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( ffa_unwrapped = a_barycenter )
print ( "Center found by arc segmentation: %s" % str ( t_ring_center ) )
