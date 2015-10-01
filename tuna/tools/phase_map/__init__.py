# -*- coding: utf-8 -*-
"""
This namespace aggregates modules related to the creation of phase maps for Fabry-Pérot interferographs.
"""

from .barycenter                            import ( barycenter_detector,
                                                     barycenter_fast )
from .find_image_center_by_symmetry         import find_image_center_by_symmetry
from .find_image_center_by_arc_segmentation import arc_segmentation_center_finder
from .fsr                                   import ( fsr_mapper )
from .high_resolution                       import ( high_resolution,
                                                     profile_processing_history )
from .noise                                 import ( noise_detector )
from .ring_borders                          import ( ring_border_detector )
from .spectrum                              import ( continuum_detector,
                                                     suppress_channel )
