from astropy.modeling.models import custom_model
from astropy.modeling.fitting import LevMarLSQFitter

import logging
from math import sqrt
import numpy
from time import time
import tuna
      
@custom_model
def airy ( cube,
           beam = 1.0,
           center_row = 0,
           center_col = 0,
           finesse = 1.,
           focal_length = 1.,
           gap = 1.,
           initial_gap = 1.,
           pixel_size = 9. ):

        log = logging.getLogger ( __name__ )
        log.info ( "beam = %f,"
                   " center_row = %d,"
                   " center_col = %d,"
                   " finesse = %f,"
                   " focal_length = %f,"
                   " gap = %f,"
                   " initial_gap = %f,"
                   " pixel_size = %f." % ( beam, center_row, center_col, finesse, 
                                           focal_length, gap, initial_gap, pixel_size ) )

        reflectivity = 0.99
        wavelength = 0.6563

        planes = cube.shape [ 0 ]
        rows   = cube.shape [ 1 ]
        cols   = cube.shape [ 2 ]

        log.debug ( "planes = %s" % str ( planes ) )
        
        center = ( center_row , center_col )

        indices = numpy.indices ( ( rows, cols ) )
        distances = numpy.sqrt ( ( indices [ 0 ] - center [ 0 ] ) ** 2 +
                                 ( indices [ 1 ] - center [ 1 ] ) ** 2 )
        grid = distances * pixel_size * ( 1.e-6 )
        theta = numpy.arctan ( grid / focal_length )

        result = numpy.ndarray ( shape = ( planes, rows, cols ) )

        for current_plane in range ( planes ):
            current_gap = initial_gap + gap * current_plane
            # function of Airy I
            airy_function = 4.0 * ( ( finesse ** 2 ) ) / ( numpy.pi ** 2 ) 
            phase = 4.0 * numpy.pi * reflectivity * current_gap * numpy.cos ( theta ) / wavelength 
            intensity = beam / ( 1. + airy_function * ( numpy.sin ( phase / 2.0 ) ) ** 2 )
            
            result [ current_plane ] = numpy.copy ( intensity )

        return result

def fit_airy ( discontinuum,
               beam,
               center,
               finesse,
               focal_length,
               gap,
               initial_gap,
               pixel_size ):
    """
    Interface function to fit an Airy model to a given input.
    """
    start = time ( )

    log = logging.getLogger ( __name__ )

    log.debug ( "initial_gap = %f" % initial_gap )
    
    # Guessing values from data:
    beam_max = numpy.amax ( discontinuum.array )

    airy_custom_model = airy ( beam = beam_max,
                               center_row = center [ 0 ], 
                               center_col = center [ 1 ],
                               finesse = finesse,
                               focal_length = focal_length,
                               gap = gap,
                               initial_gap = initial_gap,
                               pixel_size = pixel_size )
    
    LevMarLSQFitter_fit = LevMarLSQFitter ( )
    
    data = discontinuum.array
    cube = numpy.ones ( shape = data.shape )

    airy_model_fit = LevMarLSQFitter_fit ( airy_custom_model, cube, data )
    result = airy_model_fit ( cube )

    msg = "beam = %.1f, center = ( %d, %d ), finesse = %.1f, focal_length = %.3f, gap = %.6f, initial_gap = %.6f, pixel_size = %f."
    log.info ( msg % ( airy_model_fit.parameters [ 0 ],
                       airy_model_fit.parameters [ 1 ], 
                       airy_model_fit.parameters [ 2 ], 
                       airy_model_fit.parameters [ 3 ],
                       airy_model_fit.parameters [ 4 ], 
                       airy_model_fit.parameters [ 5 ],
                       airy_model_fit.parameters [ 6 ],
                       airy_model_fit.parameters [ 7 ] ) )

    log.info ( "Airy fit took %ds." % ( time ( ) - start ) )
    return tuna.io.can ( array = result )
