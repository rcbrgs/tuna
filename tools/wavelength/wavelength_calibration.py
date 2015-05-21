import logging
import math
import numpy
import threading
import time
import tuna

class wavelength_calibrator ( threading.Thread ):
    """
    Responsible for producing the wavelength calibrated cube from the phase map cube.
    """
    def __init__ ( self, unwrapped_phase_map,
                   calibration_wavelength,
                   free_spectral_range,
                   interference_order,
                   interference_reference_wavelength,
                   rings_center,
                   scanning_wavelength ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        super ( self.__class__, self ).__init__ ( )

        self.unwrapped_phase_map = unwrapped_phase_map
        
        self.calibration_wavelength = calibration_wavelength
        self.free_spectral_range = free_spectral_range
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.rings_center = rings_center
        self.scanning_wavelength = scanning_wavelength

        self.channel_width = unwrapped_phase_map.planes

        self.calibrated = None

        self.start ( )

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

    def run ( self ):
        start = time.time ( )

        self.calibrate ( )
    
        self.log.info ( "wavelength_calibration() took %ds." % ( time.time ( ) - start ) )

