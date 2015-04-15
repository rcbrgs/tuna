from tuna.data_cube.cube import cube
from math import floor, sqrt
import numpy
from tuna.io import adhoc, file_reader, fits
from .find_image_center_by_arc_segmentation import find_image_center_by_arc_segmentation
from .find_image_center_by_symmetry import find_image_center_by_symmetry
from .fsr import create_fsr_map
from .noise import create_noise_array
from tuna.tools.models.airy     import fit_airy
from tuna.tools.models.parabola import fit_parabolic_model_by_Polynomial2D
from .ring_borders import create_ring_borders_map, create_borders_to_center_distances
from tuna.tools.get_pixel_neighbours import get_pixel_neighbours
from .spectrum import create_continuum_array
from time import time
from tuna.tools.wavelength.wavelength_calibration import wavelength_calibration
from tuna.zeromq.zmq_client import zmq_client

class high_resolution ( object ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.
    Intermediary products are the binary noise, the ring borders, the regions and orders maps.
    """
    def __init__ ( self, 
                   array = numpy.ndarray,
                   bad_neighbours_threshold = 7, 
                   beam = float,
                   calibration_wavelength = None,
                   channel_subset = None,
                   channel_threshold = 1, 
                   finesse = float,
                   focal_length = float,
                   free_spectral_range = None,
                   gap = float,
                   interference_order = int,
                   interference_reference_wavelength = None,
                   log = None, 
                   noise_mask_radius = 0,
                   scanning_wavelength = None,
                   wrapped_phase_map_algorithm = None ):

        """
        Creates the phase map from raw data obtained with a Fabry-Perot instrument.

        Parameters:
        ---
        - array : the raw data. Must be a 3D numpy.ndarray.
        - bad_neighbours_threshold : how many neighbouring pixels can have a value above the threshold before the pixel itself is conidered noise.
        - channel_threshold : the distance, in "channels", that a neighbouring pixel' value can have before being considered noise.
        - noise_mas_radius : the distance from a noise pixel that will be marked as noise also (size of a circle around each noise pixel).
        - wrapped_phase_map_algorithm : name of the function to be used to compute the wrapped phase map.
        """
        super ( high_resolution, self ).__init__ ( )
        if log == None:
            zmq_client = zmq_client ( )
            self.log = zmq_client.log
        else:
            self.log = log

        self.log ( "info: Starting high_resolution pipeline." )

        try:
            array
        except NameError as e:
            self.log ( "warning: High resolution pipeline requires a valid numpy.ndarray, aborting." )
            return

        try:
            if array.ndim != 3:
                self.log ( "warning: Image does not have 3 dimensions, aborting." )
                return
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return

        self.__calibration_wavelength = calibration_wavelength
        self.__free_spectral_range = free_spectral_range
        self.__scanning_wavelength = scanning_wavelength

        if channel_subset != None:
            self.log ( "info: Using a subset of channels: %s" % str ( channel_subset ) )
            for channel in range ( array.shape [ 0 ] ):
                if channel not in channel_subset:
                    self.__array = self.substitute_channel_by_interpolation ( raw = array,
                                                                              channel = channel )
        else:
            self.__array = array

        self.continuum_array = create_continuum_array ( array = self.__array, 
                                                        continuum_tFSR_ratio = 0.25,
                                                        display = False,
                                                        log = self.log )

        self.filtered_array = numpy.ndarray ( shape = self.__array.shape )
        for dep in range ( self.__array.shape[0] ):
            self.filtered_array[dep,:,:] = self.__array[dep,:,:] - self.continuum_array

        self.wrapped_phase_map_array = wrapped_phase_map_algorithm ( array = self.filtered_array,
                                                                     log = self.log )

        self.__center = find_image_center_by_arc_segmentation ( wrapped = self.wrapped_phase_map_array,
                                                                    log = self.log )

        self.binary_noise_array = create_noise_array ( array = self.wrapped_phase_map_array, 
                                                       bad_neighbours_threshold = bad_neighbours_threshold, 
                                                       channel_threshold = channel_threshold, 
                                                       log = self.log,
                                                       noise_mask_radius = noise_mask_radius )

        self.__borders_to_center_distances = create_borders_to_center_distances ( log = self.log, 
                                                                                  array = self.wrapped_phase_map_array,
                                                                                  center = self.__center,
                                                                                  noise_array = self.binary_noise_array )

        self.__fsr = create_fsr_map ( distances = self.__borders_to_center_distances,
                                      center = self.__center,
                                      log = self.log,
                                      wrapped = self.wrapped_phase_map_array )

        self.order_array = self.__fsr.astype ( dtype = numpy.float64 )

        self.create_unwrapped_phase_map_array ( )

        self.__parabolic_coefficients, self.__parabolic_model_Polynomial2D = fit_parabolic_model_by_Polynomial2D ( center = self.__center, log = self.log, noise = self.binary_noise_array, unwrapped = self.unwrapped_phase_map )

        self.verify_parabolic_model ( )

        # Airy
        self.__airy = fit_airy ( log = self.log,
                                   beam = beam,
                                   center = self.__center,
                                   discontinuum = self.filtered_array,
                                   finesse = finesse,
                                   focal_length = focal_length,
                                   gap = gap )

        # Wavelength calibration
        self.log ( "debug: self.__calibration_wavelength == %s" % str ( self.__calibration_wavelength ) )
        self.__wavelength_calibrated = None
        self.log ( "debug: self.unwrapped_phase_map.ndim == %d" % self.unwrapped_phase_map.ndim )
        self.__unwrapped = cube ( log = self.log,
                                  data = self.unwrapped_phase_map,
                                  calibration_wavelength = self.__calibration_wavelength,
                                  free_spectral_range = self.__free_spectral_range,
                                  scanning_wavelength = self.__scanning_wavelength )
            
        self.__wavelength_calibrated = wavelength_calibration ( log = self.log,
                                                                channel_width = self.__array.shape [ 0 ],
                                                                interference_order = interference_order,
                                                                interference_reference_wavelength = interference_reference_wavelength,
                                                                unwrapped_phase_map = self.__unwrapped )
        
    def create_unwrapped_phase_map_array ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        start = time ( )

        max_x = self.wrapped_phase_map_array.shape[0]
        max_y = self.wrapped_phase_map_array.shape[1]
        max_channel = numpy.amax ( self.wrapped_phase_map_array )
        min_channel = numpy.amin ( self.wrapped_phase_map_array )
        #self.log ( "max_channel = %d" % max_channel )
        #self.log ( "min_channel = %d" % min_channel )

        self.unwrapped_phase_map = numpy.zeros ( shape = self.wrapped_phase_map_array.shape )
        self.log ( "debug: self.unwrapped_phase_map.ndim == %d" % self.unwrapped_phase_map.ndim )

        for x in range ( max_x ):
            for y in range ( max_y ):
                self.unwrapped_phase_map[x][y] = self.wrapped_phase_map_array[x][y] + max_channel * float ( self.order_array[x][y] )
                    
        max_channel = numpy.amax ( self.unwrapped_phase_map )
        min_channel = numpy.amin ( self.unwrapped_phase_map )
        #self.log ( "After unwrapping:" )
        #self.log ( "max_channel = %d" % max_channel )
        #self.log ( "min_channel = %d" % min_channel )

        self.log ( "info: create_unwrapped_phase_map_array() took %ds." % ( time ( ) - start ) )

    def get_airy ( self ):
        return self.__airy

    def get_array ( self ):
        """
        Returns the raw data array (same as the input).
        """
        return self.__array

    def get_binary_noise_array ( self ):
        """
        Returns the binary noise.
        """
        try:
            return self.binary_noise_array
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None

    def get_borders_to_center_distances ( self ):
        """
        Returns the array containing the distances from each border pixel to the tuned center of the array.
        """
        try:
            return self.__borders_to_center_distances
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None

    def get_continuum_array ( self ):
        """
        Returns the continuum array.
        """
        try:
            return self.continuum_array
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None        

    def get_filtered ( self ):
        return self.filtered_array

    def get_order_array ( self ):
        """
        Return the relative FSR map.
        """
        try:
            return self.order_array
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None

    def get_parabolic_Polynomial2D_model ( self ):
        """
        Returns a parabolic model of the data.
        """
        return self.__parabolic_model_Polynomial2D

    def get_parabolic_Polynomial2D_coefficients ( self ):
        return self.__parabolic_coefficients

    def get_unwrapped_phase_map_array ( self ):
        try: 
            return self.unwrapped_phase_map
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None

    def get_wavelength_calibrated ( self ):
        #return self.__wavelength_calibrated.get_array ( )
        if self.__wavelength_calibrated != None:
            return self.__wavelength_calibrated.get_array ( )
        else:
            self.log ( "warning: self.__wavelength_calibrated == None." )
            return None

    def get_wrapped_phase_map_array ( self ):
        """
        Returns the phase map.
        """
        try:
            return self.wrapped_phase_map_array
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None

    def get_ring_borders_array ( self ):
        """
        Returns the ring borders.
        """
        return self.ring_borders_array

    def substitute_channel_by_interpolation ( self, 
                                              channel = int,
                                              raw = numpy.ndarray ):
        """
        For each pixel in a cube's slice, substitute the value by the interpolation of the values of the neighbouring slices.
        """
        deps = raw.shape [ 0 ]
        left_channel  = ( channel - 1 + deps ) % deps
        right_channel = ( channel + 1 ) % deps
        raw [ channel ] = ( raw [ left_channel ] + raw [ right_channel ] ) / 2
        return raw

    def verify_parabolic_model ( self ):
        self.log ( "info: Ratio between 2nd degree coefficients is: %f" % ( self.__parabolic_coefficients [ 'x2y0' ] / 
                                                                            self.__parabolic_coefficients [ 'x0y2' ] ) )

def create_max_channel_map ( self, array = numpy.ndarray ):
    """
    Uses numpy.argmax to return the 2D array with the maxima along the depth of a 3D cube.
    Notice that numpy currently returns the index of the first maximum if there are several maxima.
    """
    return numpy.argmax ( array, axis = 0 )
