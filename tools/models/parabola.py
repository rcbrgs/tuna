from math import sqrt
import numpy
from time import time

class parabola ( object ):
    """
    Responsible for generating parabolic models and the fitting of models to data.
    """
    def __init__ ( self, iit_center = ( int, int ), log = print, ffa_noise = numpy.ndarray, ffa_unwrapped = numpy.ndarray ):
        super ( parabola, self ).__init__ ( )
        self.__iit_center = iit_center
        self.log = log
        self.__ffa_model = None
        self.__ffa_noise = ffa_noise
        self.__ffa_unwrapped = ffa_unwrapped

    def create_model_map_by_guess ( self ):
        """
        Generate a numpy array with the current parameters.
        """
        i_max_rows = self.__ffa_unwrapped.shape [ 0 ]
        i_max_cols = self.__ffa_unwrapped.shape [ 1 ]
        self.estimate_alpha ( )
        self.estimate_beta ( )
        self.__ffa_model = numpy.ndarray ( shape = ( i_max_rows, i_max_cols ) )
        for i_row in range ( i_max_rows ):
            for i_col in range ( i_max_cols ):
                f_distance = sqrt ( ( self.__iit_center [ 0 ] - i_row ) ** 2 +
                                    ( self.__iit_center [ 1 ] - i_col ) ** 2 )
                self.__ffa_model [ i_row ] [ i_col ] = self.__alpha + self.__beta * ( f_distance ** 2 )

    def create_model_map_by_polyfit ( self ):
        """
        Generate a numpy array with the current parameters.
        """
        i_max_rows = self.__ffa_unwrapped.shape [ 0 ]
        i_max_cols = self.__ffa_unwrapped.shape [ 1 ]
        fa_x_dimension = numpy.arange ( i_max_cols, dtype = numpy.float64 )
        #ffa_noiseless_unwrapped = numpy.where ( self.__ffa_noise == 0, self.__ffa_unwrapped, numpy.zeros ( shape = self.__ffa_unwrapped.shape ) )
        #ffa_coefficients = numpy.polynomial.polynomial.polyfit ( fa_x_dimension, ffa_noiseless_unwrapped, 2 )
        ffa_coefficients = numpy.polynomial.polynomial.polyfit ( fa_x_dimension, self.__ffa_unwrapped, 2 )

        self.__ffa_model = numpy.ndarray ( shape = ( i_max_rows, i_max_cols ) )
        for i_row in range ( i_max_rows ):
            for i_col in range ( i_max_cols ):
                f_distance = sqrt ( ( self.__iit_center [ 0 ] - i_row ) ** 2 +
                                    ( self.__iit_center [ 1 ] - i_col ) ** 2 )
                self.__ffa_model [ i_row ] [ i_col ] = ( ffa_coefficients [ 0 ] [ i_col ] +
                                                         #ffa_coefficients [ 1 ] [ i_col ] * f_distance +
                                                         ffa_coefficients [ 2 ] [ i_col ] * ( f_distance ** 2 ) )

    def estimate_alpha ( self ):
        """
        Since a + b r^2 = signal, at the center: a = signal.
        """
        self.__alpha = self.__ffa_unwrapped [ self.__iit_center [ 0 ] ] [ self.__iit_center [ 1 ] ]

    def estimate_beta ( self ):
        """
        Supposing alpha has been estimated, an initial beta can be found by selecting some pixel offcenter.
        """
        iit_offcenter = ( int ( self.__iit_center [ 0 ] / 2 ), 
                          int ( self.__iit_center [ 1 ] / 2 ) )

        f_signal = self.__ffa_unwrapped [ iit_offcenter [ 0 ] ] [ iit_offcenter [ 1 ] ]
        f_r = sqrt ( ( self.__iit_center [ 0 ] - iit_offcenter [ 0 ] ) ** 2 +
                     ( self.__iit_center [ 1 ] - iit_offcenter [ 1 ] ) ** 2 )
        self.__beta = ( f_signal - self.__alpha ) / ( f_r ** 2 )

    def get_model_map ( self ):
        return self.__ffa_model

def fit_parabolic_model_by_polyfit ( iit_center = ( int, int ), log = print, ffa_noise = numpy.ndarray, ffa_unwrapped = numpy.ndarray ):
    """
    Interface function to fit a parabolic model to a given input.
    """
    start = time ( )
    log ( "fit_parabolic_model", end = '' )

    o_parabola = parabola ( iit_center = iit_center, log = log, ffa_noise = ffa_noise, ffa_unwrapped = ffa_unwrapped )
    o_parabola.create_model_map_by_polyfit ( )

    log ( " %ds." % ( time ( ) - start ) )
    return o_parabola.get_model_map ( )

def fit_parabolic_model_by_guess ( iit_center = ( int, int ), log = print, ffa_noise = numpy.ndarray, ffa_unwrapped = numpy.ndarray ):
    """
    Interface function to fit a parabolic model to a given input.
    """
    start = time ( )
    log ( "fit_parabolic_model", end = '' )

    o_parabola = parabola ( iit_center = iit_center, log = log, ffa_noise = ffa_noise, ffa_unwrapped = ffa_unwrapped )
    o_parabola.create_model_map_by_guess ( )

    log ( " %ds." % ( time ( ) - start ) )
    return o_parabola.get_model_map ( )
