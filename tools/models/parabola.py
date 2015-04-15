from astropy.modeling import models
from astropy.modeling.fitting import NonLinearLSQFitter as LevMarLSQFitter
#from astropy.modeling.fitting import LevMarLSQFitter
from math import sqrt
import numpy
from time import time
import warnings

class parabola ( object ):
    """
    Responsible for generating parabolic models and the fitting of models to data.
    """
    def __init__ ( self, 
                   noise = numpy.ndarray, 
                   unwrapped = numpy.ndarray,
                   center = ( int, int ), 
                   log = print ):
        super ( parabola, self ).__init__ ( )
        self.__center = center
        self.log = log
        self.__model = None
        self.__noise = noise
        self.__unwrapped = unwrapped

    def create_model_map_by_Polynomial2D ( self ):
        """
        Generate a numpy array with the current parameters.
        """
        i_max_rows = self.__unwrapped.shape [ 0 ]
        i_max_cols = self.__unwrapped.shape [ 1 ]
        iia_y_dimension, iia_x_dimension = numpy.mgrid [ : i_max_rows, : i_max_cols ]

        Polynomial2D_model = models.Polynomial2D ( degree = 2 )
        LevMarLSQFitter_fit = LevMarLSQFitter ( )
        with warnings.catch_warnings ( ):
            warnings.simplefilter ( 'ignore' )
            polynomial_fit = LevMarLSQFitter_fit ( Polynomial2D_model, iia_x_dimension, iia_y_dimension, self.__unwrapped )
        #print ( str ( polynomial_fit ) )
        #print ( str ( polynomial_fit.parameters ) )
        self.__coefficients = { }
        self.__coefficients['x0y0'] = polynomial_fit.parameters [ 0 ]
        self.__coefficients['x1y0'] = polynomial_fit.parameters [ 1 ]
        self.__coefficients['x2y0'] = polynomial_fit.parameters [ 2 ]
        self.__coefficients['x0y1'] = polynomial_fit.parameters [ 3 ]
        self.__coefficients['x0y2'] = polynomial_fit.parameters [ 4 ]
        self.__coefficients['x1y1'] = polynomial_fit.parameters [ 5 ]
        #print ( self.__coefficients )
        self.__model = polynomial_fit ( iia_x_dimension, iia_y_dimension )

    def get_center ( self ):
        return ( numpy.argmin ( self.__model [ :, 0 ] ), numpy.argmin ( self.__model [ 0, : ] ) )

    def get_coefficients ( self ):
        return self.__coefficients

    def get_model_map ( self ):
        return self.__model

def fit_parabolic_model_by_Polynomial2D ( center = ( int, int ), 
                                          log = print, 
                                          noise = numpy.ndarray, 
                                          unwrapped = numpy.ndarray ):
    """
    Interface function to fit a parabolic model to a given input.
    """
    start = time ( )

    parabola = parabola ( center = center, log = log, noise = noise, unwrapped = unwrapped )
    parabola.create_model_map_by_Polynomial2D ( )
    log ( "info: parabola.get_center() = %s" % str ( parabola.get_center ( ) ) )

    log ( "info: fit_parabolic_model() took %ds." % ( time ( ) - start ) )
    return parabola.get_coefficients ( ), parabola.get_model_map ( )
