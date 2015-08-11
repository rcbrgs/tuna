import IPython
import logging
import math
import numpy
import threading
import time
import tuna

class high_resolution ( threading.Thread ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.
    Intermediary products are:
    - continuum
    - discontinuum
    - wrapped_phase_map
    - noise
    - borders_to_center_distances
    - order_map
    - unwrapped_phase_map
    - parabolic_fit
    - airy_fit
    - airy_fit_residue
    - substituted_channels
    - wavelength_calibrated
    """
    def __init__ ( self,
                   calibration_wavelength,
                   finesse,
                   free_spectral_range,
                   interference_order,
                   interference_reference_wavelength,
                   pixel_size,
                   scanning_wavelength,
                   tuna_can,
                   wrapped_algorithm,
                   channel_subset = [ ],
                   continuum_to_FSR_ratio = 0.125,
                   dont_fit = False,
                   noise_mask_radius = 1,
                   noise_threshold = None,
                   ring_minimal_percentile = None,
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
        self.__version__ = '0.1.13'
        self.changelog = {
            '0.1.13' : "Since the plane gap is calculated, use it to get limits for per-plane airy fit.",
            '0.1.12' : "Adapting pipeline to new ring_find.",
            '0.1.11' : "Adapted sorted_rings to use new ring_find result.",
            '0.1.10' : "Added a plot() function as convenience to plot all subresults.",
            '0.1.9' : "Improved auto Airy by letting intensity and continuum be free.",
            '0.1.8' : "Improved auto Airy fit by priming fitter with channel gap values.",
            '0.1.7' : "Changed method for airy fit to fit separately each plane.",
            '0.1.6' : "Added support for ring_minimal_percentile.",
            '0.1.5' : "Added support for noise threshold parameter.",
            '0.1.4' : "Reverted to simpler method of fitting first 2 planes; works beautifully.",
            '0.1.3' : "Made default less verbose.",
            '0.1.2' : "Refactored to use new ring center finder.",
            '0.1.1' : "Using variables instead of harcoded values for inital b and gap values.",
            '0.1.0' : "Initial changelog."
            }
        super ( high_resolution, self ).__init__ ( )

        if not isinstance ( tuna_can, tuna.io.can ):
            self.log.info ( "array must be a numpy.ndarray or derivative object." )
            return
        try:
            if tuna_can.ndim != 3:
                self.log.warning ( "Image does not have 3 dimensions, aborting." )
                return
        except AttributeError as e:
            self.log.warning ( "%s, aborting." % str ( e ) )
            return
        
        self.log.info ( "Starting high_resolution pipeline." )

        """inputs:"""
        self.calibration_wavelength = calibration_wavelength
        self.channel_subset = channel_subset
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio
        self.dont_fit = dont_fit
        self.finesse = finesse
        self.free_spectral_range = free_spectral_range
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.noise_mask_radius = noise_mask_radius
        self.noise_threshold = noise_threshold
        self.pixel_size = pixel_size
        self.ring_minimal_percentile = ring_minimal_percentile
        self.scanning_wavelength = scanning_wavelength
        self.tuna_can = tuna_can
        self.unwrapped_only = unwrapped_only
        self.verify_center = verify_center
        self.wrapped_algorithm = wrapped_algorithm

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
        
        self.start ( )
        
    def run ( self ):
        continuum_detector = tuna.tools.phase_map.continuum_detector ( self.tuna_can,
                                                                       self.continuum_to_FSR_ratio )
        continuum_detector.join ( )
        self.continuum = continuum_detector.continuum

        self.discontinuum = tuna.io.can ( array = numpy.ndarray ( shape = self.tuna_can.shape ) )
        for plane in range ( self.tuna_can.planes ):
            self.discontinuum.array [ plane, : , : ] = numpy.abs ( self.tuna_can.array [ plane, : , : ] - self.continuum.array )

        wrapped_producer = self.wrapped_algorithm ( self.discontinuum )
        wrapped_producer.join ( )

        self.wrapped_phase_map = wrapped_producer.result
        self.log.debug ( "self.wrapped_phase_map.array.shape = %s" % str ( self.wrapped_phase_map.array.shape ) )

        noise_detector = tuna.tools.phase_map.noise_detector ( self.tuna_can,
                                                               self.wrapped_phase_map, 
                                                               self.noise_mask_radius,
                                                               self.noise_threshold )
        noise_detector.join ( )
        self.noise = noise_detector.noise

        self.find_rings = tuna.tools.find_rings ( self.tuna_can.array, 2 )
        center = ( self.find_rings [ 'ring_fit_parameters' ] [ 0 ] [ 0 ],
                   self.find_rings [ 'ring_fit_parameters' ] [ 0 ] [ 1 ] )
        self.rings_center = center
        
        if self.verify_center != None:
            true_center = self.verify_center [ 0 ]
            threshold = self.verify_center [ 1 ]
            difference = math.sqrt ( ( center [ 0 ] - true_center [ 0 ] ) ** 2 + \
                                     ( center [ 1 ] - true_center [ 1 ] ) ** 2 )
            if difference >= threshold:
                return

        if self.dont_fit == False:
            sorted_radii = sorted ( [ self.find_rings [ 'ring_fit_parameters' ] [ 0 ] [ 2 ],
                                      self.find_rings [ 'ring_fit_parameters' ] [ 1 ] [ 2 ] ] )
            self.log.info ( "sorted_radii = {}".format (
                [ "{:.2f}".format ( radius ) for radius in sorted_radii ] ) )
            
            initial_b_ratio = tuna.tools.estimate_b_ratio ( sorted_radii [ : 2 ],
                                                            [ self.interference_order,
                                                              self.interference_order - 1 ] )
            self.log.debug ( "initial_b_ratio = {}".format ( initial_b_ratio ) )
            initial_gap = self.calibration_wavelength * self.interference_order * \
                          math.sqrt ( 1 + initial_b_ratio**2 * sorted_radii [ 0 ] ** 2 ) / 2
            self.log.info ( "inital_gap = {:.2e} microns".format ( initial_gap ) )
            
            parinfo_initial = [ ]
            parbase = { 'fixed' : False, 'limits' : ( initial_b_ratio * 0.9, initial_b_ratio * 1.1 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( center [ 0 ] - 50,
                                                      center [ 0 ] + 50 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( center [ 1 ] - 50,
                                                      center [ 1 ] + 50 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( self.finesse * 0.9, self.finesse * 1.1 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( initial_gap - self.calibration_wavelength / 4,
                                                      initial_gap + self.calibration_wavelength / 4 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo_initial.append ( parbase )

            airy_fitter_0 = tuna.models.airy_fitter ( initial_b_ratio,
                                                      center [ 0 ],
                                                      center [ 1 ],
                                                      self.tuna_can.array [ 0 ],
                                                      self.finesse,
                                                      initial_gap,
                                                      self.calibration_wavelength,
                                                      mpyfit_parinfo = parinfo_initial )

            airy_fitter_0.join ( )
            airy_fit = numpy.ndarray ( shape = self.tuna_can.shape )
            airy_fit [ 0 ] = airy_fitter_0.fit.array
            
            b_ratio     = airy_fitter_0.parameters [ 0 ]
            center_col  = airy_fitter_0.parameters [ 1 ]
            center_row  = airy_fitter_0.parameters [ 2 ]
            finesse     = airy_fitter_0.parameters [ 4 ]
            initial_gap = airy_fitter_0.parameters [ 5 ]
            
            parinfo = [ ]
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo.append ( parbase )
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( initial_gap - self.calibration_wavelength / 4,
                                                      initial_gap + self.calibration_wavelength / 4 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo.append ( parbase )

            airy_fitter_1 = tuna.models.airy_fitter ( b_ratio,
                                                      center_col,
                                                      center_row,
                                                      self.tuna_can.array [ 1 ],
                                                      finesse,
                                                      initial_gap,
                                                      self.calibration_wavelength,
                                                      mpyfit_parinfo = parinfo )
            airy_fitter_1.join ( )
            airy_fit [ 1 ] = airy_fitter_1.fit.array
            
            channel_gap = airy_fitter_1.parameters [ 5 ] - airy_fitter_0.parameters [ 5 ]
            self.log.info ( "channel_gap = {} microns.".format ( channel_gap ) )

            latest_gap = airy_fitter_1.parameters [ 5 ]
            airy_fitters = [ None, None ]
            for plane in range ( 2, self.tuna_can.planes ):
                parinfo = [ ]
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                parbase = { 'fixed' : False }
                parinfo.append ( parbase )
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                #parbase = { 'fixed'  : False,
                #            'limits' : ( initial_gap + plane * channel_gap - self.calibration_wavelength / 4,
                #                         initial_gap + plane * channel_gap + self.calibration_wavelength / 4 ) }
                parbase = { 'fixed'  : False,
                            'limits' : ( latest_gap,
                                         latest_gap + 2 * channel_gap ) }
                parinfo.append ( parbase )
                parbase = { 'fixed' : False }
                parinfo.append ( parbase )
                
                airy_fitter = tuna.models.airy_fitter ( b_ratio,
                                                        center_col,
                                                        center_row,
                                                        self.tuna_can.array [ plane ],
                                                        finesse,
                                                        latest_gap + channel_gap,
                                                        self.calibration_wavelength,
                                                        mpyfit_parinfo = parinfo )
                airy_fitters.append ( airy_fitter )
                latest_gap = airy_fitters.parameters [ 5 ]
            for plane in range ( 2, self.tuna_can.planes ):
                airy_fitters [ plane ].join ( )
                airy_fit [ plane ] = airy_fitters [ plane ].fit.array
                self.log.debug ( "Plane {} fitted.".format ( plane ) ) 
                
            self.airy_fit = tuna.io.can ( airy_fit )
            
            airy_fit_residue = self.tuna_can.array - self.airy_fit.array
            self.airy_fit_residue = tuna.io.can ( array = airy_fit_residue )
            airy_pixels = airy_fit_residue.shape [ 0 ] * airy_fit_residue.shape [ 1 ] * airy_fit_residue.shape [ 2 ] 
            self.log.info ( "Airy <|residue|> = {:.1f} photons / pixel".format (
                numpy.sum ( numpy.abs ( airy_fit_residue ) ) / airy_pixels ) )


        ring_border_detector = tuna.tools.phase_map.ring_border_detector (
            self.wrapped_phase_map,
            center,
            self.noise )
        ring_border_detector.join ( )
        self.borders_to_center_distances = ring_border_detector.distances

        fsr_mapper = tuna.tools.phase_map.fsr_mapper ( self.borders_to_center_distances,
                                                       self.wrapped_phase_map,
                                                       center )
        fsr_mapper.join ( )
        self.fsr_map = fsr_mapper.fsr
        self.order_map = tuna.io.can ( array = self.fsr_map.astype ( dtype = numpy.float64 ) )

        self.create_unwrapped_phase_map ( )
        if self.unwrapped_only == True:
            return

        if self.dont_fit == False:
            # It seems Astropy's fitters ain't thread safe, so the airy fit must be already joined.
            parabolic_fitter = tuna.models.parabolic_fitter ( self.noise,
                                                              self.unwrapped_phase_map,
                                                              center )
                                                              #self.rings_center [ 'probable_centers' ] )

        wavelength_calibrator = tuna.tools.wavelength.wavelength_calibrator ( self.unwrapped_phase_map,
                                                                              self.calibration_wavelength,
                                                                              self.free_spectral_range,
                                                                              self.interference_order,
                                                                              self.interference_reference_wavelength,
                                                                              self.tuna_can.shape [ 0 ],
                                                                              center,
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

        self.log.debug ( "wavelength_calibrated.array [ 0 ] [ 0 ] == {}".format (
            self.wavelength_calibrated.array [ 0 ] [ 0 ] ) )

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

        self.log.debug ( "Phase map 0% unwrapped." )
        last_percentage_logged = 0
        for x in range ( max_x ):
            percentage = 10 * int ( x / max_x * 10 )
            if percentage > last_percentage_logged:
                last_percentage_logged = percentage
                self.log.debug ( "Phase map %d%% unwrapped." % percentage )
            for y in range ( max_y ):
                unwrapped_phase_map [ x ] [ y ] = self.wrapped_phase_map.array [ x ] [ y ] + \
                                                  max_channel * float ( self.order_map.array [ x ] [ y ] )
        self.log.info ( "Phase map unwrapped." )

        self.unwrapped_phase_map = tuna.io.can ( array = unwrapped_phase_map )

        self.log.debug ( "create_unwrapped_phase_map() took %ds." % ( time.time ( ) - start ) )

    def verify_parabolic_model ( self ):
        self.log.debug ( "Ratio between 2nd degree coefficients is: %f" % ( self.parabolic_model [ 'x2y0' ] / 
                                                                            self.parabolic_model [ 'x0y2' ] ) )

    def plot ( self ):
        ipython = IPython.get_ipython()
        ipython.magic("matplotlib qt")

        tuna.tools.plot ( self.tuna_can.array, "original", ipython )
        tuna.tools.plot ( self.continuum.array, "continuum", ipython )
        tuna.tools.plot ( self.discontinuum.array, "discontinuum", ipython )
        tuna.tools.plot ( self.wrapped_phase_map.array, "wrapped_phase_map", ipython )
        tuna.tools.plot ( self.noise.array, "noise", ipython )
        tuna.tools.plot ( self.borders_to_center_distances.array, "borders_to_center_distances", ipython )
        tuna.tools.plot ( self.order_map.array, "order_map", ipython )
        tuna.tools.plot ( self.unwrapped_phase_map.array, "unwrapped_phase_map", ipython )
        tuna.tools.plot ( self.parabolic_fit.array, "parabolic_fit", ipython )
        tuna.tools.plot ( self.airy_fit.array, "airy_fit", ipython )
        tuna.tools.plot ( self.airy_fit_residue.array, "airy_fit_residue", ipython )
        tuna.tools.plot ( self.substituted_channels.array, "substituted_channels", ipython )
        tuna.tools.plot ( self.wavelength_calibrated.array, "wavelength_calibrated", ipython )
        
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
