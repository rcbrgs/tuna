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
        self.ndim = None
        self.tan_data = None
        if tan_data != None:
            self.ndim = tan_data.ndim
            if self.ndim == 3:
                self.tan_data = numpy.copy ( tan_data )
                self.__i_planes = self.tan_data.shape [ 0 ]
                self.__i_rows   = self.tan_data.shape [ 1 ]
                self.__i_cols   = self.tan_data.shape [ 2 ]
            elif self.ndim == 2:
                #self.tan_data = numpy.ndarray ( shape = ( 1, tan_data.shape [ 0 ], tan_data.shape [ 1 ] ) )
                self.tan_data = numpy.copy ( tan_data )
                self.__i_planes = 1
                self.__i_rows   = self.tan_data.shape [ 0 ]
                self.__i_cols   = self.tan_data.shape [ 1 ]
                #for i_row in self.get_rows_range ( ):
                #    for i_col in self.get_cols_range ( ):
                #        self.tan_data [ 0 ] [ i_row ] [ i_col ] = tan_data [ i_row ] [ i_col ]
            else:
                self.log ( "warning: Data has dimentionality different from [2, 3] dimensions." )
        self.log ( "debug: self.tan_data.ndim == %d, self.ndim == %d." % ( self.tan_data.ndim, self.ndim ) )

    def __add__ ( self,
                  o_cube ):
        if not ( self.log is o_cube.log ):
            self.log ( "debug: self.log is not o_cube.log" )

        if self.ndim != o_cube.ndim:
            self.log ( "warning: trying to sum cubes of different dimensionalities. Returning 'None' as the sum." )
            o_result_array = None
        else:
            o_result_array = self.tan_data + o_cube.tan_data

        if not ( self.__f_calibration_wavelength == o_cube.__f_calibration_wavelength ):
            self.log ( "info: Summed cubes have different calibration wavelength! Assigning 'None' as the calibration wavelength of the resulting cube." )
            f_result_calibration_wavelength = None
        else:
            f_result_calibration_wavelength = self.__f_calibration_wavelength
        
        if not ( self.__f_free_spectral_range == o_cube.__f_free_spectral_range ):
            self.log ( "info: Summed cubes have different FSR! Assigning 'None' as the FSR of the resulting cube." )
            f_result_FSR = None
        else:
            f_result_FSR = self.__f_free_spectral_range

        if not ( self.__f_scanning_wavelength == o_cube.__f_scanning_wavelength ):
            self.log ( "info: Summed cubes have different scanning wavelength! Assigning 'None' as the scanning wavelength of the resulting cube." )
            f_result_scanning_wavelength = None
        else:
            f_result_scanning_wavelength = self.__f_scanning_wavelength

        o_result = cube ( log = self.log,
                          f_calibration_wavelength = f_result_calibration_wavelength,
                          f_free_spectral_range = f_result_FSR,
                          f_scanning_wavelength = f_result_scanning_wavelength,
                          tan_data = o_result_array )

        return o_result

    def __sub__ ( self,
                  o_cube ):
        if not ( self.log is o_cube.log ):
            self.log ( "debug: self.log is not o_cube.log" )

        if self.ndim != o_cube.ndim:
            self.log ( "warning: Trying to subtract cubes of different dimensionalities (self.ndim == %d and o_cube.ndim == %d). Returning 'None' as the sum." % ( self.ndim, o_cube.ndim ) )
            o_result_array = None
        else:
            o_result_array = self.tan_data - o_cube.tan_data

        if not ( self.__f_calibration_wavelength == o_cube.__f_calibration_wavelength ):
            self.log ( "info: Summed cubes have different calibration wavelength! Assigning 'None' as the calibration wavelength of the resulting cube." )
            f_result_calibration_wavelength = None
        else:
            f_result_calibration_wavelength = self.__f_calibration_wavelength
        
        if not ( self.__f_free_spectral_range == o_cube.__f_free_spectral_range ):
            self.log ( "info: Summed cubes have different FSR! Assigning 'None' as the FSR of the resulting cube." )
            f_result_FSR = None
        else:
            f_result_FSR = self.__f_free_spectral_range

        if not ( self.__f_scanning_wavelength == o_cube.__f_scanning_wavelength ):
            self.log ( "info: Summed cubes have different scanning wavelength! Assigning 'None' as the scanning wavelength of the resulting cube." )
            f_result_scanning_wavelength = None
        else:
            f_result_scanning_wavelength = self.__f_scanning_wavelength

        o_result = cube ( log = self.log,
                          f_calibration_wavelength = f_result_calibration_wavelength,
                          f_free_spectral_range = f_result_FSR,
                          f_scanning_wavelength = f_result_scanning_wavelength,
                          tan_data = o_result_array )

        return o_result

    def get_array ( self ):
        return self.tan_data

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
