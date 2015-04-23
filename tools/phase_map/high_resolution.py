from math import floor, sqrt
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
                   interference_order,
                   interference_reference_wavelength,
                   scanning_wavelength,
                   tuna_can,
                   bad_neighbours_threshold = 7, 
                   channel_subset = [ ],
                   channel_threshold = 1, 
                   continuum_to_FSR_ratio = 0.125,
                   noise_mask_radius = 1 ):

        """
        Creates the phase map from raw data obtained with a Fabry-Perot instrument.

        Parameters:
        ---
        - array : the raw data. Must be a 3D numpy.ndarray.
        - bad_neighbours_threshold : how many neighbouring pixels can have a value above the threshold before the pixel itself is conidered noise.
        - channel_threshold : the distance, in "channels", that a neighbouring pixel' value can have before being considered noise.
        - noise_mas_radius : the distance from a noise pixel that will be marked as noise also (size of a circle around each noise pixel).
        """
        super ( high_resolution, self ).__init__ ( )
        self.zmq_client = tuna.zeromq.zmq_client ( )
        self.log = self.zmq_client.log 

        self.log ( "info: Starting high_resolution pipeline." )

        if not isinstance ( tuna_can, tuna.io.can ):
            self.log ( "info: array must be a numpy.ndarray or derivative object." )
            return

        try:
            if tuna_can.ndim != 3:
                self.log ( "warning: Image does not have 3 dimensions, aborting." )
                return
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return

        """inputs:"""
        self.bad_neighbours_threshold = bad_neighbours_threshold
        self.beam = beam
        self.calibration_wavelength = calibration_wavelength
        self.channel_subset = channel_subset
        self.channel_threshold = channel_threshold
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio
        self.finesse = finesse
        self.focal_length = focal_length
        self.free_spectral_range = free_spectral_range
        self.gap = gap
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.noise_mask_radius = noise_mask_radius
        self.scanning_wavelength = scanning_wavelength
        self.tuna_can = tuna_can

        """outputs:"""
        self.airy_fit = None
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
        self.continuum = tuna.tools.phase_map.detect_continuum ( log = self.log,
                                                                 array = self.tuna_can.array, 
                                                                 continuum_to_FSR_ratio = self.continuum_to_FSR_ratio )

        self.discontinuum = numpy.ndarray ( shape = self.tuna_can.shape )
        for plane in range ( self.tuna_can.planes ):
            self.discontinuum [ plane, : , : ] = self.tuna_can.array [ plane, : , : ] - self.continuum.array

        self.wrapped_phase_map = tuna.tools.phase_map.detect_barycenters ( log = self.log,
                                                                           array = self.discontinuum )

        self.rings_center = tuna.tools.phase_map.find_image_center_by_arc_segmentation ( log = self.log,
                                                                                         wrapped = self.wrapped_phase_map )

        self.noise = tuna.tools.phase_map.detect_noise ( log = self.log,
                                                         array = self.wrapped_phase_map, 
                                                         bad_neighbours_threshold = self.bad_neighbours_threshold, 
                                                         channel_threshold = self.channel_threshold, 
                                                         noise_mask_radius = self.noise_mask_radius )

        self.borders_to_center_distances = tuna.tools.phase_map.create_borders_to_center_distances ( log = self.log, 
                                                                                                     array = self.wrapped_phase_map,
                                                                                                     center = self.rings_center,
                                                                                                     noise_array = self.noise )

        self.fsr_map = tuna.tools.phase_map.create_fsr_map ( log = self.log,
                                                             distances = self.borders_to_center_distances,
                                                             center = self.rings_center,
                                                             wrapped = self.wrapped_phase_map )

        self.order_map = self.fsr_map.astype ( dtype = numpy.float64 )

        self.create_unwrapped_phase_map ( )

        self.parabolic_model, self.parabolic_fit = tuna.tools.models.fit_parabolic_model_by_Polynomial2D ( log = self.log, 
                                                                                                           center = self.rings_center, 
                                                                                                           noise = self.noise, 
                                                                                                           unwrapped = self.unwrapped_phase_map )
        self.verify_parabolic_model ( )

        self.airy_fit = tuna.tools.models.fit_airy ( log = self.log,
                                                     beam = self.beam,
                                                     center = self.rings_center,
                                                     discontinuum = self.discontinuum,
                                                     finesse = self.finesse,
                                                     focal_length = self.focal_length,
                                                     gap = self.gap )
        
        if self.channel_subset != [ ]:            
            self.log ( "info: Substituting channels: %s" % str ( self.channel_subset ) )
            self.substituted_channels = numpy.copy ( self.tuna_can )
            for channel in range ( self.tuna_can.planes ):
                if channel in self.channel_subset:
                    self.substituted_channels [ plane ] = numpy.copy ( self.airy_fit [ plane ] )

        #self.wavelength_calibrated = tuna.tools.wavelength.calibration ( log = self.log,
        #                                                                 channel_width = self.tuna_can.planes,
        #                                                                 interference_order = self.interference_order,
        #                                                                 interference_reference_wavelength = self.interference_reference_wavelength,
        #                                                                 unwrapped_phase_map = self.unwrapped_phase_map )
        
    def create_unwrapped_phase_map ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        start = time.time ( )

        max_x = self.wrapped_phase_map.shape[0]
        max_y = self.wrapped_phase_map.shape[1]
        max_channel = numpy.amax ( self.wrapped_phase_map )
        min_channel = numpy.amin ( self.wrapped_phase_map )
        #self.log ( "max_channel = %d" % max_channel )
        #self.log ( "min_channel = %d" % min_channel )

        self.unwrapped_phase_map = numpy.zeros ( shape = self.wrapped_phase_map.shape )
        self.log ( "debug: self.unwrapped_phase_map.ndim == %d" % self.unwrapped_phase_map.ndim )

        self.log ( "info: phase map 0% unwrapped." )
        last_percentage_logged = 0
        for x in range ( max_x ):
            percentage = 10 * int ( x / max_x * 10 )
            if percentage > last_percentage_logged:
                last_percentage_logged = percentage
                self.log ( "info: phase map %d%% unwrapped." % percentage )
            for y in range ( max_y ):
                self.unwrapped_phase_map[x][y] = self.wrapped_phase_map[x][y] + max_channel * float ( self.order_map [ x ] [ y ] )
        self.log ( "info: phase map 100% unwrapped." )

        max_channel = numpy.amax ( self.unwrapped_phase_map )
        min_channel = numpy.amin ( self.unwrapped_phase_map )

        self.log ( "info: create_unwrapped_phase_map() took %ds." % ( time.time ( ) - start ) )

    def verify_parabolic_model ( self ):
        self.log ( "info: Ratio between 2nd degree coefficients is: %f" % ( self.parabolic_model [ 'x2y0' ] / 
                                                                            self.parabolic_model [ 'x0y2' ] ) )
