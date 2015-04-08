from astropy.modeling import ( Parametric2DModel,
                               Parameter,
                               format_input )
from astropy.modeling.fitting import NonLinearLSQFitter as LevMarLSQFitter
#from astropy.modeling.fitting import LevMarLSQFitter
from math import sqrt
import numpy
from time import time

class airy_model ( Parametric2DModel ):
    """
    Airy model for Astropy. Produces a 2D slice from parameters that should correspond to an 
    idealized Fabry-Perot interferometer spectrograph.
    Originally written by Benoît Epinat.
    
    Parameters
    ----------
    
    beam         : intensity of light
    finesse      :
    focal_length :
    gap          : microns between the étalons
    """

    beam = Parameter ( 'beam' )
    finesse = Parameter ( 'finesse' )
    focal_length = Parameter ( 'focal_length' )
    gap = Parameter ( 'gap' )
    
    def __init__ ( self,
#                   log = print,
                   beam = 1.,
                   finesse = 15,
                   focal_length = 0.1,
                   gap = 1.,

                   center = ( int, int ), 
                   discontinuum = numpy.ndarray,
                   **constraints ):

        super ( airy_model, self ).__init__ ( beam = beam,
                                              finesse = finesse,
                                              focal_length = focal_length,
                                              gap = gap,
                                              **constraints )
        self.log = print
        
        self.__center = center
        self.__discontinuum = numpy.copy ( discontinuum )
        self.__deps = self.__discontinuum.shape [ 0 ]
        self.__rows = self.__discontinuum.shape [ 1 ]
        self.__cols = self.__discontinuum.shape [ 2 ]
        
        self.__pixel_size = 9
        self.__reflectivity = 0.99
       
    @staticmethod
    def eval ( x,
               y,
               beam,
               finesse,
               focal_length,
               gap ):

        pixel_size = 9
        reflectivity = 0.99
        wavelength = 0.6563

        rows = x.shape [ 0 ]
        cols = y.shape [ 1 ]
        
        center = ( 218, 253 )

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

def fit_Airy ( t_center = ( int, int ), 
               f_max_distance = None,
               f_min_distance = None,
               log = print, 
               a_filtered = numpy.ndarray ):
    """
    Interface function to fit an Airy model to a given input.
    """
    start = time ( )

    airy_custom_model = airy_model ( center = t_center, 
#                                     log = log, 
                                     discontinuum = a_filtered )
    
    airy_custom_model.beam = 100.
    airy_custom_model.beam.fixed = True
    airy_custom_model.focal_length = 0.1
    airy_custom_model.focal_length.fixed = True
    airy_custom_model.finesse = 15
    airy_custom_model.finesse.fixed = True

    LevMarLSQFitter_fit = LevMarLSQFitter ( )
    
    y, x = numpy.mgrid [ : a_filtered.shape [ 1 ], : a_filtered.shape [ 2 ] ]
    #log ( "debug: x.shape = %s" % str ( x.shape ) )
    #log ( "debug: y.shape = %s" % str ( y.shape ) )
    #log ( "debug: x = %s" % str ( x ) )
    #log ( "debug: y = %s" % str ( y ) )
    
    result = numpy.zeros ( shape = a_filtered.shape )
        
    for dep in range ( a_filtered.shape [ 0 ] ):
        #with warnings.catch_warnings ( ):
        #    warnings.simplefilter ( 'ignore' )
        data = a_filtered [ dep ]
        #log ( "debug: data.shape = %s" % str ( data.shape ) )
        #log ( "debug: data = %s" % str ( data ) )
        airy_custom_model.gap = 1904 + dep * 0.01
        #airy_custom_model.gap.fixed = True
        airy_model_fit = LevMarLSQFitter_fit ( airy_custom_model, x, y, data )
        #log ( "debug: airy_model_fit [ 'message' ] = %s" % str ( airy_model_fit [ 'message' ] ) )
        result [ dep ] = airy_model_fit ( x, y )
        #log ( "debug: result [ dep ] = %s" % str ( result [ dep ] ) )
        log ( "debug: For plane %d, Airy fit parameters are: beam = %s, finesse = %s, focal_length = %s, gap = %s" % ( dep, str ( airy_model_fit.parameters [ 0 ] ), str ( airy_model_fit.parameters [ 1 ] ), str ( airy_model_fit.parameters [ 2 ] ), str ( airy_model_fit.parameters [ 3 ] ) ) )

    log ( "info: Airy fit took %ds." % ( time ( ) - start ) )
    return result
