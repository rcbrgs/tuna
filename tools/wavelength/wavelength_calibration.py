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
    def __init__ ( self,
                   unwrapped_phase_map,
                   calibration_wavelength,
                   free_spectral_range,
                   interference_order,
                   interference_reference_wavelength,
                   number_of_channels,
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
        self.number_of_channels = number_of_channels
        self.rings_center = rings_center
        self.scanning_wavelength = scanning_wavelength

        self.channel_width = number_of_channels

        self.calibrated = None

        self.start ( )

    def calibrate ( self ):
        """
        Goal is to discover the value of the wavelength at the apex of the parabola that fits the data.
        """
        self.log.info ( "self.interference_order = %f" % self.interference_order )
        self.log.info ( "self.interference_reference_wavelength = %f" % self.interference_reference_wavelength )
        self.log.info ( "self.calibration_wavelength = %f" % self.calibration_wavelength )
        order_calibration = round ( self.interference_order * self.interference_reference_wavelength / self.calibration_wavelength )
        self.log.info ( "order_calibration = %f" % order_calibration )
        order_scanning = round ( self.interference_order * self.interference_reference_wavelength / self.scanning_wavelength )
        self.log.info ( "order_scanning = %f" % order_scanning )
        calculated_FSR = self.scanning_wavelength / order_scanning
        self.log.info ( "input FSR = %f, calculated FSR = %f" % ( self.free_spectral_range, 
                                                                calculated_FSR ) )

        decalage = self.channel_width * ( 0.5 - ( self.scanning_wavelength - 
                                                  self.calibration_wavelength * ( order_calibration / order_scanning ) ) / self.free_spectral_range )
        self.log.info ( "decalage = %f" % decalage )
        calibrated = numpy.copy ( self.unwrapped_phase_map.array )
        calibrated -= decalage

        if ( self.rings_center [ 0 ] < 0 or
             self.rings_center [ 1 ] < 0 or
             self.rings_center [ 0 ] > self.unwrapped_phase_map.array.shape [ 0 ] or
             self.rings_center [ 1 ] > self.unwrapped_phase_map.array.shape [ 1 ] ):
            self.log.error ( "Cannot wavelength-calibrate when the center is not a valid pixel! Copying the unwrapped phase map as the result." )
            self.calibrated = tuna.io.can ( array = self.unwrapped_phase_map.array )
            return

        self.log.info ( "self.number_of_channels = %d" % self.number_of_channels )
        if calibrated [ self.rings_center [ 0 ] ] [ self.rings_center [ 1 ] ] < 0:
            ceiling_offset = math.ceil ( - numpy.amin ( calibrated ) / self.number_of_channels ) * self.number_of_channels
            self.log.info ( "ceiling_offset = %f" % ceiling_offset )
            calibrated += ceiling_offset

        if calibrated [ self.rings_center [ 0 ] ] [ self.rings_center [ 1 ] ] > self.number_of_channels:
            floor_offset = math.floor (  numpy.amin ( calibrated ) / self.number_of_channels ) * self.number_of_channels
            calibrated -= floor_offset
            self.log.info ( "floor_offset = %f" % floor_offset )

        self.log.debug ( "self.unwrapped_phase_map.get_array().ndim == %d" % self.unwrapped_phase_map.ndim )
        self.log.debug ( "calibrated.ndim == %d" % calibrated.ndim )

        self.calibrated = tuna.io.can ( array = calibrated )

    def run ( self ):
        start = time.time ( )

        self.calibrate ( )
    
        self.log.info ( "wavelength_calibration() took %ds." % ( time.time ( ) - start ) )

