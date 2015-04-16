#!/bin/env ipython3

import tuna

# find_center_by_symmetry:
can = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G092.AD3' )
raw  = can.array
ring_center = tuna.tools.phase_map.find_image_center_by_symmetry ( data = raw )
print ( "Center found by symmetry: %s" % str ( ring_center ) )

# find_center_by_arcs:
barycenter = tuna.tools.phase_map.create_barycenter_array ( array = raw )
ring_center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( wrapped = barycenter )
print ( "Center found by arc segmentation: %s" % str ( ring_center ) )
