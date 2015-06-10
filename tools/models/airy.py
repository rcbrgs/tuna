from astropy.modeling.models import custom_model
from astropy.modeling.fitting import LevMarLSQFitter

import logging
from math import sqrt
import numpy
import threading
import time
import tuna
      
def airy_function ( cube,
                    beam = 1.0,
                    center_row = 0,
                    center_col = 0,
                    finesse = 1.,
                    focal_length = 1.,
                    gap = 1.,
                    initial_gap = 1.,
                    pixel_size = 9. ):
    log = logging.getLogger ( __name__ )
    log.debug ( "beam = %f,"
                " center_row = %d,"
                " center_col = %d,"
                " finesse = %f,"
                " focal_length = %f,"
                " gap = %f,"
                " initial_gap = %f,"
                " pixel_size = %f." % ( beam, center_row, center_col, finesse, 
                                        focal_length, gap, initial_gap, pixel_size ) )

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
        airy_function_I = 4.0 * ( ( finesse ** 2 ) ) / ( numpy.pi ** 2 ) 
        phase = 4.0 * numpy.pi * current_gap * numpy.cos ( theta ) / wavelength 
        intensity = beam / ( 1. + airy_function_I * ( numpy.sin ( phase / 2.0 ) ) ** 2 )
        
        result [ current_plane ] = numpy.copy ( intensity )

    return result

@custom_model
def airy_fittable_function ( cube,
                             beam = 1.0,
                             center_row = 0,
                             center_col = 0,
                             finesse = 1.,
                             focal_length = 1.,
                             gap = 1.,
                             initial_gap = 1.,
                             pixel_size = 9. ):
    return airy_function ( cube,
                           beam,
                           center_row,
                           center_col,
                           finesse,
                           focal_length,
                           gap,
                           initial_gap,
                           pixel_size )

class airy_fitter ( threading.Thread ):
    def __init__ ( self, discontinuum, beam, center, finesse, focal_length,
                   gap, initial_gap, pixel_size ):
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )
        
        self.discontinuum = discontinuum
        self.beam = beam
        self.center = center
        self.finesse = finesse
        self.focal_length = focal_length
        self.gap = gap
        self.initial_gap = initial_gap
        self.pixel_size = pixel_size

        self.fit = None
        self.parameters = None

        self.start ( )

    def run ( self ):
        """
        Interface function to fit an Airy model to a given input.
        """
        start = time.time ( )

        self.log.debug ( "initial_gap = %f" % self.initial_gap )

        airy_custom_model = airy_fittable_function ( beam = self.beam,
                                                     center_row = self.center [ 0 ], 
                                                     center_col = self.center [ 1 ],
                                                     finesse = self.finesse,
                                                     focal_length = self.focal_length,
                                                     gap = self.gap,
                                                     initial_gap = self.initial_gap,
                                                     pixel_size = self.pixel_size )

        airy_custom_model.finesse.fixed = True
        airy_custom_model.focal_length.fixed = True
        airy_custom_model.gap.fixed = True
        airy_custom_model.pixel_size.fixed = True
        airy_custom_model.center_row.fixed = True
        airy_custom_model.center_col.fixed = True
    
        LevMarLSQFitter_fit = LevMarLSQFitter ( )
    
        data = self.discontinuum.array
        cube = numpy.ones ( shape = data.shape )

        airy_model_fit = LevMarLSQFitter_fit ( airy_custom_model, cube, data )
        result = airy_model_fit ( cube )
        self.parameters = airy_model_fit.parameters

        msg = "beam = %.1f, center = ( %d, %d ), finesse = %.1f, focal_length = %.3f, gap = %.6f, initial_gap = %.6f, pixel_size = %f."
        self.log.warning ( msg % ( airy_model_fit.parameters [ 0 ],
                                airy_model_fit.parameters [ 1 ], 
                                airy_model_fit.parameters [ 2 ], 
                                airy_model_fit.parameters [ 3 ],
                                airy_model_fit.parameters [ 4 ], 
                                airy_model_fit.parameters [ 5 ],
                                airy_model_fit.parameters [ 6 ],
                                airy_model_fit.parameters [ 7 ] ) )

        self.log.info ( "Airy fit took %ds." % ( time.time ( ) - start ) )
        self.fit = tuna.io.can ( result )
