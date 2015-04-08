from tuna.data_cube.cube import cube
from math import floor, sqrt
import numpy
from tuna.io import adhoc, file_reader, fits
from .find_image_center_by_arc_segmentation import find_image_center_by_arc_segmentation
from .find_image_center_by_symmetry import find_image_center_by_symmetry
from .fsr import create_fsr_map
from .noise import create_noise_array
from tuna.tools.models.airy     import fit_Airy
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
                   f_calibration_wavelength = None,
                   il_channel_subset = None,
                   channel_threshold = 1, 
                   finesse = float,
                   focal_length = float,
                   f_free_spectral_range = None,
                   gap = float,
                   i_interference_order = int,
                   f_interference_reference_wavelength = None,
                   log = None, 
                   noise_mask_radius = 0,
                   f_scanning_wavelength = None,
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
            o_zmq_client = zmq_client ( )
            self.log = o_zmq_client.log
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

        self.__f_calibration_wavelength = f_calibration_wavelength
        self.__f_free_spectral_range = f_free_spectral_range
        self.__f_scanning_wavelength = f_scanning_wavelength

        if il_channel_subset != None:
            self.log ( "info: Using a subset of channels: %s" % str ( il_channel_subset ) )
            for i_channel in range ( array.shape [ 0 ] ):
                if i_channel not in il_channel_subset:
                    self.__array = self.substitute_channel_by_interpolation ( a_raw = array,
                                                                              i_channel = i_channel )
        else:
            self.__array = array

        self.continuum_array = create_continuum_array ( array = self.__array, 
                                                        f_continuum_to_FSR_ratio = 0.25,
                                                        b_display = False,
                                                        log = self.log )

        self.filtered_array = numpy.ndarray ( shape = self.__array.shape )
        for dep in range ( self.__array.shape[0] ):
            self.filtered_array[dep,:,:] = self.__array[dep,:,:] - self.continuum_array

        self.wrapped_phase_map_array = wrapped_phase_map_algorithm ( array = self.filtered_array,
                                                                     log = self.log )

        self.__iit_center = find_image_center_by_arc_segmentation ( ffa_unwrapped = self.wrapped_phase_map_array,
                                                                    log = self.log )

        self.binary_noise_array = create_noise_array ( array = self.wrapped_phase_map_array, 
                                                       bad_neighbours_threshold = bad_neighbours_threshold, 
                                                       channel_threshold = channel_threshold, 
                                                       log = self.log,
                                                       noise_mask_radius = noise_mask_radius )

        self.__fa_borders_to_center_distances = create_borders_to_center_distances ( log = self.log, 
                                                                                     array = self.wrapped_phase_map_array,
                                                                                     iit_center = self.__iit_center,
                                                                                     noise_array = self.binary_noise_array )

        self.__ia_fsr = create_fsr_map ( fa_distances = self.__fa_borders_to_center_distances,
                                         iit_center = self.__iit_center,
                                         log = self.log,
                                         fa_wrapped = self.wrapped_phase_map_array )

        self.order_array = self.__ia_fsr.astype ( dtype = numpy.float64 )

        self.create_unwrapped_phase_map_array ( )

        self.__parabolic_coefficients, self.__ffa_parabolic_model_Polynomial2D = fit_parabolic_model_by_Polynomial2D ( iit_center = self.__iit_center,
                                                                                                                       log = self.log,
                                                                                                                       ffa_noise = self.binary_noise_array,
                                                                                                                       ffa_unwrapped = self.unwrapped_phase_map )

        self.verify_parabolic_model ( )

        # Airy
        self.__a_airy = fit_Airy ( log = self.log,
                                   beam = beam,
                                   center = self.__iit_center,
                                   discontinuum = self.filtered_array,
                                   finesse = finesse,
                                   focal_length = focal_length,
                                   gap = gap )

        # Wavelength calibration
        self.log ( "debug: self.__f_calibration_wavelength == %s" % str ( self.__f_calibration_wavelength ) )
        self.__o_wavelength_calibrated = None
        self.log ( "debug: self.unwrapped_phase_map.ndim == %d" % self.unwrapped_phase_map.ndim )
        self.__o_unwrapped = cube ( log = self.log,
                                    tan_data = self.unwrapped_phase_map,
                                    f_calibration_wavelength = self.__f_calibration_wavelength,
                                    f_free_spectral_range = self.__f_free_spectral_range,
                                    f_scanning_wavelength = self.__f_scanning_wavelength )
            
        self.__o_wavelength_calibrated = wavelength_calibration ( log = self.log,
                                                                  i_channel_width = self.__array.shape [ 0 ],
                                                                  i_interference_order = i_interference_order,
                                                                  f_interference_reference_wavelength = f_interference_reference_wavelength,
                                                                  o_unwrapped_phase_map = self.__o_unwrapped )

    def create_unwrapped_phase_map_array ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        i_start = time ( )

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

        self.log ( "info: create_unwrapped_phase_map_array() took %ds." % ( time ( ) - i_start ) )

    def get_airy ( self ):
        return self.__a_airy

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
            return self.__fa_borders_to_center_distances
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
        return self.__ffa_parabolic_model_Polynomial2D

    def get_parabolic_Polynomial2D_coefficients ( self ):
        return self.__parabolic_coefficients

    def get_unwrapped_phase_map_array ( self ):
        try: 
            return self.unwrapped_phase_map
        except AttributeError as e:
            self.log ( "warning: %s, aborting." % str ( e ) )
            return None

    def get_wavelength_calibrated ( self ):
        #return self.__o_wavelength_calibrated.get_array ( )
        if self.__o_wavelength_calibrated != None:
            return self.__o_wavelength_calibrated.get_array ( )
        else:
            self.log ( "warning: self.__o_wavelength_calibrated == None." )
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
                                              i_channel = int,
                                              a_raw = numpy.ndarray ):
        """
        For each pixel in a cube's slice, substitute the value by the interpolation of the values of the neighbouring slices.
        """
        i_deps = a_raw.shape [ 0 ]
        i_left_channel  = ( i_channel - 1 + i_deps ) % i_deps
        i_right_channel = ( i_channel + 1 ) % i_deps
        a_raw [ i_channel ] = ( a_raw [ i_left_channel ] + a_raw [ i_right_channel ] ) / 2
        return a_raw

    def verify_parabolic_model ( self ):
        self.log ( "info: Ratio between 2nd degree coefficients is: %f" % ( self.__parabolic_coefficients [ 'x2y0' ] / 
                                                                            self.__parabolic_coefficients [ 'x0y2' ] ) )

def create_max_channel_map ( self, array = numpy.ndarray ):
    """
    Uses numpy.argmax to return the 2D array with the maxima along the depth of a 3D cube.
    Notice that numpy currently returns the index of the first maximum if there are several maxima.
    """
    return numpy.argmax ( array, axis = 0 )
