from astropy.modeling import ( Parametric2DModel,
                               Parameter,
                               format_input )
from astropy.modeling.fitting import NonLinearLSQFitter as LevMarLSQFitter
#from astropy.modeling.fitting import LevMarLSQFitter
from math import sqrt
import numpy
from time import time
import tuna

class airy ( Parametric2DModel ):
    """
    Airy model for Astropy. Produces a 2D slice from parameters that should correspond to an 
    idealized Fabry-Perot interferometer spectrograph.
    Originally written by Benoît Epinat.
    
    Parameters
    ----------
    
    beam         : intensity of light
    center_row
    center_col
    finesse      :
    focal_length :
    gap          : microns between the étalons
    """

    beam = Parameter ( 'beam' )
    center_row = Parameter ( 'center_row' )
    center_col = Parameter ( 'center_col' )
    finesse = Parameter ( 'finesse' )
    focal_length = Parameter ( 'focal_length' )
    gap = Parameter ( 'gap' )
    
    def __init__ ( self,
#                   log = print,
                   beam = 1.,
                   center_row = 0,
                   center_col = 0,
                   finesse = 15,
                   focal_length = 0.1,
                   gap = 1.,
                   **constraints ):

        super ( airy, self ).__init__ ( beam = beam,
                                              center_row = center_row,
                                              center_col = center_col,
                                              finesse = finesse,
                                              focal_length = focal_length,
                                              gap = gap,
                                              **constraints )
        self.log = print
       
    @staticmethod
    def eval ( x,
               y,
               beam,
               center_row,
               center_col,
               finesse,
               focal_length,
               gap ):

        pixel_size = 9
        reflectivity = 0.99
        wavelength = 0.6563

        rows = x.shape [ 0 ]
        cols = y.shape [ 1 ]
        
        center = ( center_row , center_col )

        indices = numpy.indices ( ( rows, cols ) )
        distances = numpy.sqrt ( ( indices [ 0 ] - center [ 0 ] ) ** 2 +
                                 ( indices [ 1 ] - center [ 1 ] ) ** 2 )
        grid = distances * pixel_size * ( 1.e-6 )
        theta = numpy.arctan ( grid / focal_length )

        result = numpy.zeros ( shape = ( rows, cols ) )

        # function of Airy I
        airy_function = 4.0 * ( ( finesse ** 2 ) ) / ( numpy.pi ** 2 ) 
        phase = 4.0 * numpy.pi * reflectivity * gap * numpy.cos ( theta ) / wavelength 
        intensity = beam / ( 1. + airy_function * ( numpy.sin ( phase / 2.0 ) ) ** 2 )

        return intensity

def fit_airy ( discontinuum,
               beam = float,
               center = ( int, int ), 
               finesse = float,
               focal_length = float,
               gap = float,
               log = print ):
    """
    Interface function to fit an Airy model to a given input.
    """
    start = time ( )

    airy_custom_model = airy ( beam = beam,
                               center_row = center [ 0 ], 
                               center_col = center [ 1 ],
                               finesse = finesse,
                               focal_length = focal_length,
                               gap = gap )
    
    LevMarLSQFitter_fit = LevMarLSQFitter ( )
    
    y, x = numpy.mgrid [ : discontinuum.shape [ 1 ], : discontinuum.shape [ 2 ] ]
    result = numpy.zeros ( shape = discontinuum.shape )
        
    for dep in range ( discontinuum.shape [ 0 ] ):
        #with warnings.catch_warnings ( ):
        #    warnings.simplefilter ( 'ignore' )
        airy_custom_model.beam = beam
        airy_custom_model.center_row = center [ 0 ]
        airy_custom_model.center_row.fixed = True
        airy_custom_model.center_col = center [ 1 ]
        airy_custom_model.center_col.fixed = True
        airy_custom_model.finesse = finesse
        airy_custom_model.finesse.fixed = True
        airy_custom_model.focal_length = focal_length
        airy_custom_model.gap = gap

        data = discontinuum.array [ dep ]
        airy_model_fit = LevMarLSQFitter_fit ( airy_custom_model, x, y, data )
        result [ dep ] = airy_model_fit ( x, y )
        msg = "debug: plane %d, beam = %.1f, finesse = %.1f, focal_length = %.3f, gap = %.2f"
        log ( msg % ( dep, 
                      airy_model_fit.parameters [ 0 ], 
                      airy_model_fit.parameters [ 3 ],
                      airy_model_fit.parameters [ 4 ], 
                      airy_model_fit.parameters [ 5 ] ) )

    log ( "info: Airy fit took %ds." % ( time ( ) - start ) )
    return tuna.io.can ( log = log,
                         array = result )

