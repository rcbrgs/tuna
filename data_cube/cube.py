"""
Responsible for storing data cubes.
"""

import numpy

class cube ( object ):
    """
    Responsible for storing data cubes.
    """
    def __init__ ( self,
                   log = print,
                   f_calibration_wavelength = None,
                   f_free_spectral_range = None,
                   tan_data = None,
                   f_scanning_wavelength = None ):
        super ( cube, self ).__init__ ( )
        self.__f_calibration_wavelength = f_calibration_wavelength
        self.__f_free_spectral_range = f_free_spectral_range
        self.log = log
        self.__f_scanning_wavelength = f_scanning_wavelength
        if tan_data != None:
            self.__ndim = tan_data.ndim
            if self.__ndim == 3:
                self.__tan_data = numpy.copy ( tan_data )
                self.__i_planes = self.__tan_data.shape [ 0 ]
                self.__i_rows   = self.__tan_data.shape [ 1 ]
                self.__i_cols   = self.__tan_data.shape [ 2 ]
            elif self.__ndim == 2:
                self.__tan_data = numpy.ndarray ( shape = ( 1, tan_data.shape [ 0 ], tan_data.shape [ 1 ] ) )
                self.__i_planes = 1
                self.__i_rows   = self.__tan_data.shape [ 1 ]
                self.__i_cols   = self.__tan_data.shape [ 2 ]
                for i_row in self.get_rows_range ( ):
                    for i_col in self.get_cols_range ( ):
                        self.__tan_data [ 0 ] [ i_row ] [ i_col ] = tan_data [ i_row ] [ i_col ]
            else:
                self.log ( "Data has dimentionality different from [2, 3] dimensions." )

    def get_array ( self ):
        return self.__tan_data

    def get_calibration_wavelength ( self ):
        return self.__f_calibration_wavelength

    def get_cols ( self ):
        return self.__i_cols

    def get_cols_range ( self ):
        return range ( self.__i_cols )

    def get_free_spectral_range ( self ):
        return self.__f_free_spectral_range

    def get_planes ( self ):
        return self.__i_planes

    def get_planes_range ( self ):
        return range ( self.__i_planes )

    def get_rows ( self ):
        return self.__i_rows

    def get_rows_range ( self ):
        return range ( self.__i_rows )

    def get_scanning_wavelength ( self ):
        return self.__f_scanning_wavelength

    def set_calibration_wavelength ( self, 
                                     f_calibration_wavelength = None ):
        self.__f_calibration_wavelength = f_calibration_wavelength

    def set_free_spectral_range ( self,
                                  f_free_spectral_range = None ):
        self.__f_free_spectral_range = f_free_spectral_range
        
    def set_scanning_wavelength ( self,
                                  f_wavelength = None ):
        self.__f_scanning_wavelength = f_wavelength
