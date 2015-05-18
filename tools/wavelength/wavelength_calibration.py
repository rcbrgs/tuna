import logging
import math
import numpy
import time
import tuna

class calibration ( object ):
    """
    Responsible for producing the wavelength calibrated cube from the phase map cube.
    """
    def __init__ ( self,
                   rings_center,
                   calibration_wavelength = None,
                   free_spectral_range = None,
                   interference_order = None,
                   interference_reference_wavelength = None,
                   scanning_wavelength = None,
                   unwrapped_phase_map = None ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        super ( calibration, self ).__init__ ( )

        self.calibrated = None
        self.calibration_wavelength = calibration_wavelength
        self.channel_width = unwrapped_phase_map.planes
        self.free_spectral_range = free_spectral_range
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.rings_center = rings_center
        self.scanning_wavelength = scanning_wavelength
        self.unwrapped_phase_map = unwrapped_phase_map

    def calibrate ( self ):
        """
        Goal is to discover the value of the wavelength at the apex of the parabola that fits the data.
        """
        calculated_FSR = self.scanning_wavelength / self.interference_order
        self.log.info ( "input FSR = %f, calculated FSR = %f" % ( self.free_spectral_range, 
                                                                   calculated_FSR ) )
        order_calibration = int ( self.interference_order * self.interference_reference_wavelength / self.calibration_wavelength )
        order_scanning = int ( self.interference_order * self.interference_reference_wavelength / self.scanning_wavelength )
        decalage = self.channel_width * ( 0.5 - ( self.scanning_wavelength - 
                                                  self.calibration_wavelength * ( order_calibration / order_scanning ) / self.free_spectral_range ) )
        self.log.info ( "decalage = %f" % decalage )
        calibrated = numpy.copy ( self.unwrapped_phase_map.array )
        calibrated -= decalage

        if calibrated [ self.rings_center [ 0 ] ] [ self.rings_center [ 1 ] ] < 0:
            ceiling_offset = math.ceil ( - numpy.amin ( calibrated ) / self.unwrapped_phase_map.planes ) * self.unwrapped_phase_map.planes
            calibrated += ceiling_offset
            self.log.info ( "ceiling_offset = %f" % ceiling_offset )

        if calibrated [ self.rings_center [ 0 ] ] [ self.rings_center [ 1 ] ] > self.unwrapped_phase_map.planes:
            floor_offset = math.floor (  numpy.amin ( calibrated ) / self.unwrapped_phase_map.planes ) * self.unwrapped_phase_map.planes
            calibrated -= floor_offset
            self.log.info ( "floor_offset = %f" % floor_offset )

        self.log.debug ( "self.unwrapped_phase_map.get_array().ndim == %d" % self.unwrapped_phase_map.ndim )
        self.log.debug ( "calibrated.ndim == %d" % calibrated.ndim )

        self.calibrated = tuna.io.can ( array = calibrated )

def wavelength_calibration ( rings_center,
                             calibration_wavelength = None,
                             free_spectral_range = None,
                             interference_order = None,
                             interference_reference_wavelength = None,
                             scanning_wavelength = None,
                             unwrapped_phase_map = None ):
    start = time.time ( )
    log = logging.getLogger ( __name__ )

    calibration_tool = calibration ( rings_center,
                                     calibration_wavelength = calibration_wavelength,
                                     free_spectral_range = free_spectral_range,
                                     interference_order = interference_order,
                                     interference_reference_wavelength = interference_reference_wavelength,
                                     scanning_wavelength = scanning_wavelength,
                                     unwrapped_phase_map = unwrapped_phase_map )
    calibration_tool.calibrate ( )
    
    log.info ( "wavelength_calibration() took %ds." % ( time.time ( ) - start ) )
    return calibration_tool.calibrated
