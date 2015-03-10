from math import sqrt
import numpy
from time import time

class airy ( object ):
    """
    Responsible for generating parabolic models and the fitting of models to data.
    """
    def __init__ ( self, 
                   t_center = ( int, int ), 
                   log = print,
                   a_filtered = numpy.ndarray ):
        super ( airy, self ).__init__ ( )
        self.__t_center = t_center
        self.__a_fit = None
        self.log = log
        self.__a_filtered = numpy.copy ( a_filtered )

    def fit ( self,
              I0 = 1., 
              lamb = 0.6563, 
              F = 15, 
              n = 1, 
              fcam = 0.1, 
              pix = 9. ):
        """
        Airy function in order to compute a ring
        Originally written by Benoît Epinat.
        
        Parameters
        ----------
        
        I0   = 1.     : intensity
        lamb = 0.6563 : wavelength (micron)
        F    = 15     : finesse
        n    = 1      : reflexion index
        fcam = 0.1    : focal length of the camera (meter)
        pix  = 9.     : pixel size (micron)
        """

        i_deps = self.__a_filtered.shape [ 0 ]
        i_rows = self.__a_filtered.shape [ 1 ]
        i_cols = self.__a_filtered.shape [ 2 ]
    
        # task: find the f_min_distance that produces the correct number of rings
        # task: find the f_min_distance that has the innermost ring with the same distance as the raw data
        f_min_distance = 1904
        # task: find the f_max_distance
        f_max_distance = 1926

        #a_fit = numpy.zeros ( shape = ( 22, self.__a_filtered.shape [ 1 ], self.__a_filtered.shape [ 2 ] ) )
        a_fit = numpy.zeros ( shape = self.__a_filtered.shape )

        #for i_dep in range ( a_fit.shape [ 0 ] ):
        for i_dep in range ( i_deps ):
            # spacing between the two FP plates (micron)
            f_spacing = f_min_distance + ( float ( i_dep ) / float ( i_deps - 1 ) ) * ( f_max_distance - f_min_distance )
            image = numpy.zeros ( shape = ( i_rows, i_cols ) )
            # we need the indices of the pixels in image
            ind = numpy.indices ( ( i_rows, i_cols ) )
            # we use numpy sqrt function because we compute on arrays
            rpix = numpy.sqrt ( ( ind [ 0 ] - self.__t_center [ 0 ] ) ** 2 +
                                ( ind [ 1 ] - self.__t_center [ 1 ] ) ** 2 )
            # radius unit = meter
            r = rpix * pix * ( 1.e-6 )
            theta = numpy.arctan ( r / fcam )
            # function of Airy I
            f = 4.0 * ( ( F ** 2 ) ) / ( numpy.pi ** 2 ) 
            phi = 2.0 * numpy.pi * ( ( 2 * n * f_spacing * ( numpy.cos ( theta ) ) ) / ( lamb ) )
            I = I0 / ( 1. + f * ( numpy.sin ( phi / 2.0 ) ) ** 2 )
            # append to cube
            a_fit [ i_dep ] = I

        self.__a_fit = a_fit

    def get_fit ( self ):
        if self.__a_fit == None:
            self.fit ( )
        return self.__a_fit

def fit_Airy ( t_center = ( int, int ), 
               log = print, 
               a_filtered = numpy.ndarray ):
    """
    Interface function to fit an Airy model to a given input.
    """
    start = time ( )

    o_model = airy ( t_center = t_center, 
                     log = log, 
                     a_filtered = a_filtered )
    o_model.fit ( )

    log ( "info: Airy o_model() took %ds." % ( time ( ) - start ) )
    return o_model.get_fit ( )
