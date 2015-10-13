"""
This namespace aggregates modules that are meant to be called as library routines; in other words, if the user is expected to use some tool "X" contained in Tuna, he is expected to call it as "tuna.tools.X", or a shorthand form of that if the user creates an alias for it.
"""

__version__ = "0.1.0"
__changelog__ = {
    "0.1.0" : { "Tuna" : "0.15.0",
                "Comment" : "Added overscan module to this namespace. Added overscan.no_overscan function to this namespace." }
    }

import tuna.tools.phase_map
import tuna.tools.wavelength

from .barycenter                     import ( barycenter_geometry,
                                              barycenter_polynomial_fit )
from .continuum                      import ( continuum_detector )
from .estimate_b_ratio               import estimate_b_ratio
from .find_lowest_nonnull_percentile import find_lowest_nonnull_percentile
from .find_rings                     import find_rings
from .fsr                            import ( fsr_mapper )
from .geometry                       import ( calculate_distance )
from .get_connected_points           import get_connected_points
from .get_connected_region           import get_connected_region
from .get_pixel_neighbours           import get_pixel_neighbours
from .hash_functions                 import get_hash_from_array
from .noise                          import noise_detector
from .overscan                       import ( no_overscan,
                                              remove_elements )
try:
    from .plot                 import ( plot,
                                        plot_high_res )
except ImportError:
    pass
