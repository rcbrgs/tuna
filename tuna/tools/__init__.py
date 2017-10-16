"""
This namespace aggregates modules that are meant to be called as library routines; in other words, if the user is expected to use some tool "X" contained in Tuna, he is expected to call it as "tuna.tools.X", or a shorthand form of that if the user creates an alias for it.
"""

#import tuna.tools.phase_map
#import tuna.tools.wavelength

#from .barycenter                     import ( barycenter_geometry,
#                                              barycenter_polynomial_fit )
#from .continuum                      import ( continuum_detector )
#from .estimate_b_ratio               import estimate_b_ratio
#from .find_lowest_nonnull_percentile import find_lowest_nonnull_percentile
#from .fsr                            import ( fsr_mapper )
#from .geometry                       import ( calculate_distance )
#from .get_connected_points           import get_connected_points
#from .get_connected_region           import get_connected_region
#from .get_pixel_neighbours           import get_pixel_neighbours
from .hash_functions                 import get_hash_from_array
#from .noise                          import noise_detector
#from .overscan                       import ( no_overscan,
#                                              remove_elements )
try:
    from .plot                 import ( plot,
                                        plot_high_res,
                                        plot_spectral_rings )
except ImportError as e:
    print ( "An exception happened while importing the plot module. It will be ignored, but calls to tuna.tools.plot functions will fail. Exception. {}".format ( e ) )

#from .spectral_rings_fitter          import find_rings as spectral_rings_fitter
