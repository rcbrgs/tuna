from tuna.data_cube.cube import cube
import numpy
from time import time

class calibration ( object ):
    """
    Responsible for producing the wavelength calibrated cube from the phase map cube.
    """
    def __init__ ( self,
                   log = print,
                   channel_width = None,
                   interference_order = None,
                   interference_reference_wavelength = None,
                   unwrapped_phase_map = None ):
        super ( calibration, self ).__init__ ( )
        self.__calibrated = None
        self.__calibration_wavelength = unwrapped_phase_map.get_calibration_wavelength ( )
        self.__channel_width = channel_width
        self.__interference_order = interference_order
        self.__interference_reference_wavelength = interference_reference_wavelength
        self.log = log
        self.__scanning_wavelength = unwrapped_phase_map.get_scanning_wavelength ( )
        self.__unwrapped_phase_map = unwrapped_phase_map

    def calibrate ( self ):
        """
        Goal is to discover the value of the wavelength at the apex of the parabola that fits the data.
        """
        if self.__channel_width == None:
            self.__channel_width = self.__unwrapped_phase_map.get_planes ( )
        self.log ( "debug: self.__channel_width = %d" % self.__channel_width )
        calibration_wavelength = self.__unwrapped_phase_map.get_calibration_wavelength ( )
        free_spectral_range    = self.__unwrapped_phase_map.get_free_spectral_range ( )
        scanning_wavelength    = self.__unwrapped_phase_map.get_scanning_wavelength ( )
        order_calibration = int ( self.__interference_order * self.__interference_reference_wavelength / self.__calibration_wavelength )
        order_scanning = int ( self.__interference_order * self.__interference_reference_wavelength / self.__scanning_wavelength )
        decalage = self.__channel_width * ( 0.5 - ( self.__scanning_wavelength - 
                                                        self.__calibration_wavelength * ( order_calibration / order_scanning ) / free_spectral_range ) )
        self.log ( "info: decalage = %f" % decalage )
        offset = 0
        self.log ( "info: offset = %f" % offset )
        self.log ( "debug: self.__unwrapped_phase_map.get_array().ndim == %d" % self.__unwrapped_phase_map.get_array().ndim )
        calibrated = numpy.copy ( self.__unwrapped_phase_map.get_array ( ) )
        calibrated -= decalage
        calibrated += offset
        self.log ( "debug: calibrated.ndim == %d" % calibrated.ndim )

        self.__calibrated = cube ( log = self.log,
                                   data = calibrated )

    def get_cube ( self ):
        if self.__calibrated == None:
            self.calibrate ( )
        return self.__calibrated

def wavelength_calibration ( log = print,
                             channel_width = None,
                             interference_order = None,
                             interference_reference_wavelength = None,
                             unwrapped_phase_map = None ):
    start = time ( )
    calibration_tool = calibration ( log = log,
                                     channel_width = channel_width,
                                     interference_order = interference_order,
                                     interference_reference_wavelength = interference_reference_wavelength,
                                     unwrapped_phase_map = unwrapped_phase_map )
    calibration_tool.calibrate ( )
    log ( "info: wavelength_calibration() took %ds." % ( time ( ) - start ) )
    return calibration_tool.get_cube ( )
