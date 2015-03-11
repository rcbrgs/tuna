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
              f_beam         = 1., 
              f_wavelength   = 0.6563, 
              f_finesse      = 15, 
              f_reflectivity = 0.99, 
              f_focal_length = 0.1, 
              f_pixel_size   = 9. ):
        """
        Airy function in order to compute a ring
        Originally written by Benoît Epinat.
        
        Parameters
        ----------
        
        f_beam         = 1.     : intensity
        f_wavelength   = 0.6563 : wavelength (micron)
        f_finesse      = 15     : finesse
        f_reflectivity = 1      : reflexion index
        f_focal_length = 0.1    : focal length of the camera (meter)
        f_pixel_size   = 9.     : pixel size (micron)
        """

        i_deps = self.__a_filtered.shape [ 0 ]
        i_rows = self.__a_filtered.shape [ 1 ]
        i_cols = self.__a_filtered.shape [ 2 ]
    
        # task: find the f_min_distance that produces the correct number of rings
        # task: find the f_min_distance that has the innermost ring with the same distance as the raw data
        f_min_distance = 1904
        # task: find the f_max_distance
        #f_max_distance = 1926
        f_max_distance = 1905

        #a_fit = numpy.zeros ( shape = ( 22, self.__a_filtered.shape [ 1 ], self.__a_filtered.shape [ 2 ] ) )
        a_fit = numpy.zeros ( shape = self.__a_filtered.shape )

        l_spacings = [ ]
        #for i_dep in range ( a_fit.shape [ 0 ] ):
        for i_dep in range ( i_deps ):
            #a_image = numpy.zeros ( shape = ( i_rows, i_cols ) )
            # we need the indices of the pixels in image
            a_indices = numpy.indices ( ( i_rows, i_cols ) )
            # we use numpy sqrt function because we compute on arrays
            a_distances = numpy.sqrt ( ( a_indices [ 0 ] - self.__t_center [ 0 ] ) ** 2 +
                                       ( a_indices [ 1 ] - self.__t_center [ 1 ] ) ** 2 )
            # radius unit = meter
            a_grid = a_distances * f_pixel_size * ( 1.e-6 )
            a_theta = numpy.arctan ( a_grid / f_focal_length )

            # spacing between the two FP plates (micron)
            #f_spacing = float ( f_min_distance + 
            #                    float ( i_dep / ( i_deps - 1 ) ) * ( f_max_distance - f_min_distance ) )
            f_spacing = float ( f_min_distance + ( i_dep / ( i_deps - 1 ) ) * ( f_max_distance - f_min_distance ) )
            l_spacings.append ( f_spacing )
            # function of Airy I
            f_airy_I = 4.0 * ( ( f_finesse ** 2 ) ) / ( numpy.pi ** 2 ) 
            f_phase = 4.0 * numpy.pi * f_reflectivity * f_spacing * numpy.cos ( a_theta ) / f_wavelength 
            f_intensity = f_beam / ( 1. + f_airy_I * ( numpy.sin ( f_phase / 2.0 ) ) ** 2 )
            # append to cube
            a_fit [ i_dep ] = f_intensity
        self.log ( "debug: l_spacings = %s" % str ( l_spacings ) )

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
