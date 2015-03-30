from astropy.modeling import ( FittableModel,
                               Parameter,
                               format_input )
#from astropy.modeling.fitting import NonLinearLSQFitter as LevMarLSQFitter
from astropy.modeling.fitting import LevMarLSQFitter
from math import sqrt
import numpy
from time import time

class airy_model ( FittableModel ):
    """
    Airy model for Astropy. Produces a 2D slice from parameters that should correspond to an 
    idealized Fabry-Perot interferometer spectrograph.
    Originally written by Benoît Epinat.
    
    Parameters
    ----------
    
    beam     : intensity of light
    distance : microns between the étalons
    finesse  :
    """

    beam = Parameter ( )
    gap = Parameter ( )
    finesse = Parameter ( )
    
    def __init__ ( self,
                   log = print,
                   center = ( int, int ), 
                   discontinuum = numpy.ndarray,
                   beam     = 1., 
                   gap = 0,
                   finesse  = 15,
                   **kwargs ):

        super ( airy_model, self ).__init__ ( beam = beam,
                                              gap = gap,
                                              finesse = finesse,
                                              **kwargs )
        self.log = log
        
        self.__center = center
        self.__discontinuum = numpy.copy ( discontinuum )
        self.__deps = self.__discontinuum.shape [ 0 ]
        self.__rows = self.__discontinuum.shape [ 1 ]
        self.__cols = self.__discontinuum.shape [ 2 ]
        
        self.__focal_length = 0.1
        self.__pixel_size = 9
        self.__reflectivity = 0.99

        self.__fit = None

        indices = numpy.indices ( ( self.__rows, self.__cols ) )
        distances = numpy.sqrt ( ( indices [ 0 ] - self.__center [ 0 ] ) ** 2 +
                                 ( indices [ 1 ] - self.__center [ 1 ] ) ** 2 )
        grid = distances * self.__pixel_size * ( 1.e-6 )
        self.__theta = numpy.arctan ( grid / self.__focal_length )
        

    def eval ( x,
               beam,
               gap,
               finesse ):

        rows = self.__a_filtered.shape [ 1 ]
        cols = self.__a_filtered.shape [ 2 ]
        
        result = numpy.zeros ( shape = ( rows, cols ) )
        # function of Airy I
        airy_function = 4.0 * ( ( finesse ** 2 ) ) / ( numpy.pi ** 2 ) 
        phase = 4.0 * numpy.pi * self.__reflectivity * gap * numpy.cos ( self.__theta ) / self.__wavelength 
        intensity = beam / ( 1. + airy_function * ( numpy.sin ( phase / 2.0 ) ) ** 2 )

        return intensity

    @format_input
    def __call__ ( self, x ):
        return self.eval ( x, *self.param_sets )
    
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
                                     log = log, 
                                     discontinuum = a_filtered )
    LevMarLSQFitter_fit = LevMarLSQFitter ( )
    
    y, x = numpy.mgrid [ : a_filtered.shape [ 1 ], : a_filtered.shape [ 0 ] ]
    
    result = numpy.zeros ( shape = a_filtered.shape )
        
    for dep in range ( a_filtered.shape [ 0 ] ):
        #with warnings.catch_warnings ( ):
        #    warnings.simplefilter ( 'ignore' )
        data = a_filtered [ dep ]
        airy_model_fit = LevMarLSQFitter_fit ( airy_custom_model, x, y, data )
        result [ dep ] = airy_model_fit ( x, y )
        log ( "debug: For plane %d, Airy fit parameters are: %s" % ( dep, str ( airy_model_fit.parameters ) ) )

    log ( "info: Airy fit took %ds." % ( time ( ) - start ) )
    return result
