"""
This module's scope is to model and fit a parabolic dsitribution to data.
"""

from astropy.modeling import models
from astropy.modeling.fitting import LevMarLSQFitter
import logging
from math import sqrt
import numpy
import threading
import time
import tuna
import warnings

class parabolic_fitter ( threading.Thread ):
    """
    This class's responsibility is to generate parabolic models and the fitting of models to data.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor signature is:

    Parameters:

    * center : tuple of 2 floats
        Containing the expected center of the interferograph.

    * noise : can
        Contains the noise corresponding to the data.

    * unwrapped : can
        Contains the data to be fitted.
    """
    def __init__ ( self, noise, unwrapped, center ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.0"
        self.changelog = {
            "0.1.0" : "Tuna 0.14.0 : updated docstrings to new style."
            }
        
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.center = center
        self.noise = noise.array
        self.unwrapped = unwrapped.array

        self.fit = None
        self.model = None
        self.coefficients = None

        self.start ( )

    def run ( self ):
        """
        This method's goal is to fit a parabolic model to a given input.
        """
        start = time.time ( )

        self.create_model_map_by_Polynomial2D ( )
        self.log.debug ( "parabolic_model.get_center() = %s" % str ( self.get_center ( ) ) )
        self.fit = tuna.io.can ( self.model )
        
        self.log.info ( "Parabolic model fitted." )
        self.log.debug ( "fit_parabolic_model_by_Polynomial2D() took %ds." % ( time.time ( ) - start ) )  

    def create_model_map_by_Polynomial2D ( self ):
        """
        This method's goal is to generate a numpy array with the current parameters.
        """
        i_max_rows = self.unwrapped.shape [ 0 ]
        i_max_cols = self.unwrapped.shape [ 1 ]
        iia_y_dimension, iia_x_dimension = numpy.mgrid [ : i_max_rows, : i_max_cols ]

        Polynomial2D_model = models.Polynomial2D ( degree = 2 )
        LevMarLSQFitter_fit = LevMarLSQFitter ( )
        with warnings.catch_warnings ( ):
            warnings.simplefilter ( 'ignore' )
            polynomial_fit = LevMarLSQFitter_fit ( Polynomial2D_model, iia_x_dimension, iia_y_dimension, self.unwrapped )
        #print ( str ( polynomial_fit ) )
        #print ( str ( polynomial_fit.parameters ) )
        self.coefficients = { }
        self.coefficients['x0y0'] = polynomial_fit.parameters [ 0 ]
        self.coefficients['x1y0'] = polynomial_fit.parameters [ 1 ]
        self.coefficients['x2y0'] = polynomial_fit.parameters [ 2 ]
        self.coefficients['x0y1'] = polynomial_fit.parameters [ 3 ]
        self.coefficients['x0y2'] = polynomial_fit.parameters [ 4 ]
        self.coefficients['x1y1'] = polynomial_fit.parameters [ 5 ]
        #print ( self.coefficients )
        self.model = polynomial_fit ( iia_x_dimension, iia_y_dimension )

    def get_center ( self ):
        """
        This method's goal is to access the coordinates for the minimum value on each axis, which should correspond to the center.

        Returns:

        * unnamed variable : tuple of 2 integers
            Containing the column and row (respectively) of the center.
        """
        return ( numpy.argmin ( self.model [ :, 0 ] ), numpy.argmin ( self.model [ 0, : ] ) )
