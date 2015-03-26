from tuna.data_cube.cube import cube
import numpy
from time import time

class calibration ( object ):
    """
    Responsible for producing the wavelength calibrated cube from the phase map cube.
    """
    def __init__ ( self,
                   log = print,
                   i_channel_width = None,
                   i_interference_order = None,
                   f_interference_reference_wavelength = None,
                   o_unwrapped_phase_map = None ):
        super ( calibration, self ).__init__ ( )
        self.__o_calibrated = None
        self.__f_calibration_wavelength = o_unwrapped_phase_map.get_calibration_wavelength ( )
        self.__i_channel_width = i_channel_width
        self.__i_interference_order = i_interference_order
        self.__f_interference_reference_wavelength = f_interference_reference_wavelength
        self.log = log
        self.__f_scanning_wavelength = o_unwrapped_phase_map.get_scanning_wavelength ( )
        self.__o_unwrapped_phase_map = o_unwrapped_phase_map

    def calibrate ( self ):
        """
        Goal is to discover the value of the wavelength at the apex of the parabola that fits the data.
        """
        if self.__i_channel_width == None:
            self.__i_channel_width = self.__o_unwrapped_phase_map.get_planes ( )
        self.log ( "debug: self.__i_channel_width = %d" % self.__i_channel_width )
        f_calibration_wavelength = self.__o_unwrapped_phase_map.get_calibration_wavelength ( )
        f_free_spectral_range    = self.__o_unwrapped_phase_map.get_free_spectral_range ( )
        f_scanning_wavelength    = self.__o_unwrapped_phase_map.get_scanning_wavelength ( )
        i_order_calibration = int ( self.__i_interference_order * self.__f_interference_reference_wavelength / self.__f_calibration_wavelength )
        i_order_scanning = int ( self.__i_interference_order * self.__f_interference_reference_wavelength / self.__f_scanning_wavelength )
        f_decalage = self.__i_channel_width * ( 0.5 - ( self.__f_scanning_wavelength - 
                                                        self.__f_calibration_wavelength * ( i_order_calibration / i_order_scanning ) / f_free_spectral_range ) )
        self.log ( "info: f_decalage = %f" % f_decalage )
        f_offset = 0
        self.log ( "info: f_offset = %f" % f_offset )
        self.log ( "debug: self.__o_unwrapped_phase_map.get_array().ndim == %d" % self.__o_unwrapped_phase_map.get_array().ndim )
        a_calibrated = numpy.copy ( self.__o_unwrapped_phase_map.get_array ( ) )
        a_calibrated -= f_decalage
        a_calibrated += f_offset
        self.log ( "debug: a_calibrated.ndim == %d" % a_calibrated.ndim )

        self.__o_calibrated = cube ( log = self.log,
                                     tan_data = a_calibrated )

    def get_cube ( self ):
        if self.__o_calibrated == None:
            self.calibrate ( )
        return self.__o_calibrated

def wavelength_calibration ( log = print,
                             i_channel_width = None,
                             i_interference_order = None,
                             f_interference_reference_wavelength = None,
                             o_unwrapped_phase_map = None ):
    i_start = time ( )
    o_calibration_tool = calibration ( log = log,
                                       i_channel_width = i_channel_width,
                                       i_interference_order = i_interference_order,
                                       f_interference_reference_wavelength = f_interference_reference_wavelength,
                                       o_unwrapped_phase_map = o_unwrapped_phase_map )
    o_calibration_tool.calibrate ( )
    log ( "info: wavelength_calibration() took %ds." % ( time ( ) - i_start ) )
    return o_calibration_tool.get_cube ( )
