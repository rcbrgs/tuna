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
                   calibration_wavelength = None,
                   free_spectral_range = None,
                   data = None,
                   scanning_wavelength = None ):
        super ( cube, self ).__init__ ( )
        self.__calibration_wavelength = calibration_wavelength
        self.__free_spectral_range = free_spectral_range
        self.log = log
        self.__scanning_wavelength = scanning_wavelength
        self.ndim = None
        self.data = None
        if data != None:
            self.ndim = data.ndim
            if self.ndim == 3:
                self.data = numpy.copy ( data )
                self.__planes = self.data.shape [ 0 ]
                self.__rows   = self.data.shape [ 1 ]
                self.__cols   = self.data.shape [ 2 ]
            elif self.ndim == 2:
                self.data = numpy.copy ( data )
                self.__planes = 1
                self.__rows   = self.data.shape [ 0 ]
                self.__cols   = self.data.shape [ 1 ]
            else:
                self.log ( "warning: Data has dimentionality different from [2, 3] dimensions." )
        self.log ( "debug: self.data.ndim == %d, self.ndim == %d." % ( self.data.ndim, self.ndim ) )

    def __add__ ( self,
                  data_cube ):
        if not ( self.log is data_cube.log ):
            self.log ( "debug: self.log is not data_cube.log" )

        if self.ndim != data_cube.ndim:
            self.log ( "warning: trying to sum cubes of different dimensionalities. Returning 'None' as the sum." )
            result = None
        else:
            result = self.data + data_cube.data

        if not ( self.__calibration_wavelength == data_cube.__calibration_wavelength ):
            self.log ( "info: Summed cubes have different calibration wavelength! Assigning 'None' as the calibration wavelength of the resulting cube." )
            result_calibration_wavelength = None
        else:
            result_calibration_wavelength = self.__calibration_wavelength
        
        if not ( self.__free_spectral_range == data_cube.__free_spectral_range ):
            self.log ( "info: Summed cubes have different FSR! Assigning 'None' as the FSR of the resulting cube." )
            result_FSR = None
        else:
            result_FSR = self.__free_spectral_range

        if not ( self.__scanning_wavelength == data_cube.__scanning_wavelength ):
            self.log ( "info: Summed cubes have different scanning wavelength! Assigning 'None' as the scanning wavelength of the resulting cube." )
            result_scanning_wavelength = None
        else:
            result_scanning_wavelength = self.__scanning_wavelength

        result_cube = cube ( log = self.log,
                             calibration_wavelength = result_calibration_wavelength,
                             free_spectral_range = result_FSR,
                             scanning_wavelength = result_scanning_wavelength,
                             data = result )

        return result_cube

    def __sub__ ( self,
                  data_cube ):
        if not ( self.log is data_cube.log ):
            self.log ( "debug: self.log is not data_cube.log" )

        if self.ndim != data_cube.ndim:
            self.log ( "warning: Trying to subtract cubes of different dimensionalities (self.ndim == %d and data_cube.ndim == %d). Returning 'None' as the sum." % ( self.ndim, data_cube.ndim ) )
            result = None
        else:
            result = self.data - data_cube.data

        if not ( self.__calibration_wavelength == data_cube.__calibration_wavelength ):
            self.log ( "info: Summed cubes have different calibration wavelength! Assigning 'None' as the calibration wavelength of the resulting cube." )
            result_calibration_wavelength = None
        else:
            result_calibration_wavelength = self.__calibration_wavelength
        
        if not ( self.__free_spectral_range == data_cube.__free_spectral_range ):
            self.log ( "info: Summed cubes have different FSR! Assigning 'None' as the FSR of the resulting cube." )
            result_FSR = None
        else:
            result_FSR = self.__free_spectral_range

        if not ( self.__scanning_wavelength == data_cube.__scanning_wavelength ):
            self.log ( "info: Summed cubes have different scanning wavelength! Assigning 'None' as the scanning wavelength of the resulting cube." )
            result_scanning_wavelength = None
        else:
            result_scanning_wavelength = self.__scanning_wavelength

        result_cube = cube ( log = self.log,
                             calibration_wavelength = result_calibration_wavelength,
                             free_spectral_range = result_FSR,
                             scanning_wavelength = result_scanning_wavelength,
                             data = result )

        return result_cube

    def get_array ( self ):
        return self.data

    def get_calibration_wavelength ( self ):
        return self.__calibration_wavelength

    def get_cols ( self ):
        return self.__cols

    def get_cols_range ( self ):
        return range ( self.__cols )

    def get_free_spectral_range ( self ):
        return self.__free_spectral_range

    def get_planes ( self ):
        return self.__planes

    def get_planes_range ( self ):
        return range ( self.__planes )

    def get_rows ( self ):
        return self.__rows

    def get_rows_range ( self ):
        return range ( self.__rows )

    def get_scanning_wavelength ( self ):
        return self.__scanning_wavelength

    def set_calibration_wavelength ( self, 
                                     calibration_wavelength = None ):
        self.__calibration_wavelength = calibration_wavelength

    def set_free_spectral_range ( self,
                                  free_spectral_range = None ):
        self.__free_spectral_range = free_spectral_range
        
    def set_scanning_wavelength ( self,
                                  f_wavelength = None ):
        self.__scanning_wavelength = f_wavelength
