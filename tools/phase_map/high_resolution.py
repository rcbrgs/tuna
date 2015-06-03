import logging
import math
import numpy
import threading
import time
import tuna

class high_resolution ( threading.Thread ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.
    Intermediary products are the binary noise, the ring borders, the regions and orders maps.
    """
    def __init__ ( self, 
                   beam,
                   calibration_wavelength,
                   finesse,
                   focal_length,
                   free_spectral_range,
                   gap,
                   initial_gap,
                   interference_order,
                   interference_reference_wavelength,
                   pixel_size,
                   scanning_wavelength,
                   tuna_can,
                   channel_subset = [ ],
                   continuum_to_FSR_ratio = 0.125,
                   dont_fit = False,
                   noise_mask_radius = 1,
                   unwrapped_only = False,
                   verify_center = None ):

        """
        Creates the phase map from raw data obtained with a Fabry-Perot instrument.

        Parameters:
        ---
        - array : the raw data. Must be a 3D numpy.ndarray.
        - noise_mask_radius : the distance from a noise pixel that will be marked as noise also (size of a circle around each noise pixel).
        """
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        super ( high_resolution, self ).__init__ ( )

        self.log.info ( "Starting high_resolution pipeline." )

        """inputs:"""
        self.beam = beam
        self.calibration_wavelength = calibration_wavelength
        self.channel_subset = channel_subset
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio
        self.dont_fit = dont_fit
        self.finesse = finesse
        self.focal_length = focal_length
        self.free_spectral_range = free_spectral_range
        self.gap = gap
        self.initial_gap = initial_gap
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.noise_mask_radius = noise_mask_radius
        self.pixel_size = pixel_size
        self.scanning_wavelength = scanning_wavelength
        self.tuna_can = tuna_can
        self.unwrapped_only = unwrapped_only
        self.verify_center = verify_center

        """outputs:"""
        self.airy_fit = None
        self.airy_fit_residue = None
        self.borders_to_center_distances = None
        self.continuum = None
        self.discontinuum = None
        self.fsr_map = None
        self.noise = None
        self.order_map = None
        self.parabolic_fit = None
        self.parabolic_model = None
        self.rings_center = None
        self.substituted_channels = None
        self.unwrapped_phase_map = None
        self.wavelength_calibrated = None
        self.wrapped_phase_map = None

    def run ( self ):
        continuum_detector = tuna.tools.phase_map.continuum_detector ( self.tuna_can,
                                                                       self.continuum_to_FSR_ratio )
        continuum_detector.join ( )
        self.continuum = continuum_detector.continuum

        self.discontinuum = tuna.io.can ( array = numpy.ndarray ( shape = self.tuna_can.shape ) )
        for plane in range ( self.tuna_can.planes ):
            self.discontinuum.array [ plane, : , : ] = numpy.abs ( self.tuna_can.array [ plane, : , : ] - self.continuum.array )

        barycenter_detector = tuna.tools.phase_map.barycenter_detector ( self.discontinuum )
        barycenter_detector.join ( )
        self.wrapped_phase_map = barycenter_detector.result

        noise_detector = tuna.tools.phase_map.noise_detector ( self.tuna_can,
                                                               self.wrapped_phase_map, 
                                                               self.noise_mask_radius )
        noise_detector.join ( )
        self.noise = noise_detector.noise

        center_finder = tuna.tools.phase_map.arc_segmentation_center_finder ( self.wrapped_phase_map,
                                                                              self.noise )
        center_finder.join ( )
        self.rings_center = center_finder.center
        if self.verify_center != None:
            true_center = self.verify_center [ 0 ]
            threshold = self.verify_center [ 1 ]
            difference = math.sqrt ( ( self.rings_center [ 0 ] - true_center [ 0 ] ) ** 2 + \
                                     ( self.rings_center [ 1 ] - true_center [ 1 ] ) ** 2 )
            if difference >= threshold:
                return

        if self.dont_fit == False:
            airy_fitter = tuna.tools.models.airy_fitter ( self.discontinuum,
                                                          self.beam,
                                                          self.rings_center,
                                                          self.finesse,
                                                          self.focal_length,
                                                          self.gap,
                                                          self.initial_gap,
                                                          self.pixel_size )

        ring_border_detector = tuna.tools.phase_map.ring_border_detector ( self.wrapped_phase_map,
                                                                           self.rings_center,
                                                                           self.noise )
        ring_border_detector.join ( )
        self.borders_to_center_distances = ring_border_detector.distances

        fsr_mapper = tuna.tools.phase_map.fsr_mapper ( self.borders_to_center_distances,
                                                       self.wrapped_phase_map,
                                                       self.rings_center )
        fsr_mapper.join ( )
        self.fsr_map = fsr_mapper.fsr
        self.order_map = tuna.io.can ( array = self.fsr_map.astype ( dtype = numpy.float64 ) )

        self.create_unwrapped_phase_map ( )
        if self.unwrapped_only == True:
            return

        if self.dont_fit == False:
            airy_fitter.join ( )
            self.airy_fit = airy_fitter.fit
            airy_fit_residue = numpy.abs ( self.tuna_can.array - self.airy_fit.array )
            self.airy_fit_residue = tuna.io.can ( array = airy_fit_residue )
            airy_pixels = airy_fit_residue.shape [ 0 ] * airy_fit_residue.shape [ 1 ] * airy_fit_residue.shape [ 2 ] 
            self.log.info ( "Airy fit residue average error = %s channels / pixel" % str ( numpy.sum ( airy_fit_residue ) / airy_pixels ) )
            # It seems Astropy's fitters ain't thread safe, so the airy fit must be already joined.
            parabolic_fitter = tuna.tools.models.parabolic_fitter ( self.noise,
                                                                    self.unwrapped_phase_map,
                                                                    self.rings_center )

        wavelength_calibrator = tuna.tools.wavelength.wavelength_calibrator ( self.unwrapped_phase_map,
                                                                              self.calibration_wavelength,
                                                                              self.free_spectral_range,
                                                                              self.interference_order,
                                                                              self.interference_reference_wavelength,
                                                                              self.tuna_can.shape [ 0 ],
                                                                              self.rings_center,
                                                                              self.scanning_wavelength )


        if self.dont_fit == False:
            substituted_channels = numpy.copy ( self.tuna_can.array )
            for channel in range ( self.tuna_can.planes ):
                if channel in self.channel_subset:
                    substituted_channels [ plane ] = numpy.copy ( self.airy_fit.array [ plane ] )
            self.substituted_channels = tuna.io.can ( array = substituted_channels )

            parabolic_fitter.join ( )
            self.parabolic_model = parabolic_fitter.coefficients
            self.parabolic_fit   = parabolic_fitter.fit
            self.verify_parabolic_model ( )

        wavelength_calibrator.join ( )
        self.wavelength_calibrated = wavelength_calibrator.calibrated

    def create_unwrapped_phase_map ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        start = time.time ( )

        max_x = self.wrapped_phase_map.array.shape[0]
        max_y = self.wrapped_phase_map.array.shape[1]
        max_channel = numpy.amax ( self.wrapped_phase_map.array )
        min_channel = numpy.amin ( self.wrapped_phase_map.array )

        unwrapped_phase_map = numpy.zeros ( shape = self.wrapped_phase_map.shape )
        self.log.debug ( "unwrapped_phase_map.ndim == %d" % unwrapped_phase_map.ndim )

        self.log.info ( "Phase map 0% unwrapped." )
        last_percentage_logged = 0
        for x in range ( max_x ):
            percentage = 10 * int ( x / max_x * 10 )
            if percentage > last_percentage_logged:
                last_percentage_logged = percentage
                self.log.info ( "Phase map %d%% unwrapped." % percentage )
            for y in range ( max_y ):
                unwrapped_phase_map [ x ] [ y ] = self.wrapped_phase_map.array [ x ] [ y ] + \
                                                  max_channel * float ( self.order_map.array [ x ] [ y ] )
        self.log.info ( "Phase map 100% unwrapped." )

        self.unwrapped_phase_map = tuna.io.can ( array = unwrapped_phase_map )

        self.log.info ( "create_unwrapped_phase_map() took %ds." % ( time.time ( ) - start ) )

    def verify_parabolic_model ( self ):
        self.log.info ( "Ratio between 2nd degree coefficients is: %f" % ( self.parabolic_model [ 'x2y0' ] / 
                                                                           self.parabolic_model [ 'x0y2' ] ) )

def high_resolution_pipeline ( beam,
                               calibration_wavelength,
                               finesse,
                               focal_length,
                               free_spectral_range,
                               gap,
                               initial_gap,
                               interference_order,
                               interference_reference_wavelength,
                               pixel_size,
                               scanning_wavelength,
                               tuna_can,
                               channel_subset = [ ],
                               continuum_to_FSR_ratio = 0.125,
                               dont_fit = False,
                               unwrapped_only = False,
                               verify_center = None,
                               noise_mask_radius = 1 ):

    log = logging.getLogger ( __name__ )

    if not isinstance ( tuna_can, tuna.io.can ):
        log.info ( "array must be a numpy.ndarray or derivative object." )
        return
    try:
        if tuna_can.ndim != 3:
            log.warning ( "Image does not have 3 dimensions, aborting." )
            return
    except AttributeError as e:
        log.warning ( "%s, aborting." % str ( e ) )
        return

    high_resolution_pipeline = high_resolution ( beam,
                                                 calibration_wavelength,
                                                 finesse,
                                                 focal_length,
                                                 free_spectral_range,
                                                 gap,
                                                 initial_gap,
                                                 interference_order,
                                                 interference_reference_wavelength,
                                                 pixel_size,
                                                 scanning_wavelength,
                                                 tuna_can,
                                                 channel_subset,
                                                 continuum_to_FSR_ratio,
                                                 dont_fit,
                                                 noise_mask_radius,
                                                 unwrapped_only,
                                                 verify_center )

    high_resolution_pipeline.start ( )
    high_resolution_pipeline.join ( )

    return high_resolution_pipeline

def profile_processing_history ( high_resolution, pixel ):
    profile = { }

    profile [ 0 ] = ( 'Original data', high_resolution.tuna_can.array [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 1 ] = ( 'Discontinuum', high_resolution.discontinuum.array [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 2 ] = ( 'Wrapped phase map', high_resolution.wrapped_phase_map.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 3 ] = ( 'Order map', high_resolution.order_map.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 4 ] = ( 'Unwrapped phase map', high_resolution.unwrapped_phase_map.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 5 ] = ( 'Parabolic fit', high_resolution.parabolic_fit.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 6 ] = ( 'Airy fit', high_resolution.airy_fit.array [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 7 ] = ( 'Wavelength', high_resolution.wavelength_calibrated.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )

    return profile
