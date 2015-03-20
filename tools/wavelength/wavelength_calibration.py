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
                   o_unwrapped_phase_map = None ):
        super ( calibration, self ).__init__ ( )
        self.__o_calibrated = None
        self.__i_channel_width = i_channel_width
        self.log = log
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
        f_decalage = self.__i_channel_width * ( 0.5 - ( f_scanning_wavelength - 
                                                        f_calibration_wavelength ** 2 / ( f_scanning_wavelength * f_free_spectral_range ) ) )
        self.log ( "info: f_decalage = %f" % f_decalage )
        f_offset = 0
        self.log ( "info: f_offset = %f" % f_offset )
        a_calibrated = numpy.copy ( self.__o_unwrapped_phase_map.get_array ( ) )
        a_calibrated -= f_decalage
        a_calibrated += f_offset

        self.__o_calibrated = cube ( log = self.log,
                                     tan_data = a_calibrated )

    def get_cube ( self ):
        if self.__o_calibrated == None:
            self.calibrate ( )
        return self.__o_calibrated

def wavelength_calibration ( log = print,
                             i_channel_width = None,
                             o_unwrapped_phase_map = None ):
    i_start = time ( )
    o_calibration_tool = calibration ( log = log,
                                       i_channel_width = i_channel_width,
                                       o_unwrapped_phase_map = o_unwrapped_phase_map )
    o_calibration_tool.calibrate ( )
    log ( "info: wavelength_calibration() took %ds." % ( time ( ) - i_start ) )
    return o_calibration_tool.get_cube ( )
