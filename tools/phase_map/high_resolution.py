from math import floor, sqrt
import numpy
from file_format import adhoc, file_reader, fits
from .find_image_center_by_arc_segmentation import find_image_center_by_arc_segmentation
from .find_image_center_by_symmetry import find_image_center_by_symmetry
from .fsr import create_fsr_map
from .noise import create_noise_array
from tools.models.parabola import fit_parabolic_model_by_Polynomial2D
from .ring_borders import create_ring_borders_map, create_borders_to_center_distances
from tools.get_pixel_neighbours import get_pixel_neighbours
from .spectrum import create_continuum_array
from time import time
from zeromq.zmq_client import zmq_client

class high_resolution ( object ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.
    Intermediary products are the binary noise, the ring borders, the regions and orders maps.
    """
    def __init__ ( self, 
                   array = numpy.ndarray,
                   bad_neighbours_threshold = 7, 
                   il_channel_subset = None,
                   channel_threshold = 1, 
                   log = None, 
                   noise_mask_radius = 0,
                   wrapped_phase_map_algorithm = None, 
                   *args, 
                   **kwargs ):
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
        super ( high_resolution, self ).__init__ ( *args, **kwargs )
        if log == None:
            o_zmq_client = zmq_client ( )
            self.log = o_zmq_client.log
        else:
            self.log = log

        self.log ( "info: Starting high_resolution pipeline." )

        if array.ndim != 3:
            self.log ( "warning: Image does not have 3 dimensions, aborting." )
            return

        if il_channel_subset != None:
            self.log ( "info: Using a subset of channels: %s" % str ( il_channel_subset ) )
            f3a_subset = numpy.ndarray ( shape = ( len ( il_channel_subset ), array.shape [ 1 ], array.shape [ 2 ] ) )
            il_sorted_subset = sorted ( il_channel_subset )
            for i_channel in range ( len ( il_sorted_subset ) ):
                f3a_subset [ i_channel ] = array [ il_sorted_subset [ i_channel ] ]
            self.__array = f3a_subset
        else:
            self.__array = array

        self.continuum_array = create_continuum_array ( array = self.__array, 
                                                        f_continuum_to_FSR_ratio = 0.25,
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

        for x in range ( max_x ):
            for y in range ( max_y ):
                self.unwrapped_phase_map[x][y] = self.wrapped_phase_map_array[x][y] + max_channel * float ( self.order_array[x][y] )
                    
        max_channel = numpy.amax ( self.unwrapped_phase_map )
        min_channel = numpy.amin ( self.unwrapped_phase_map )
        #self.log ( "After unwrapping:" )
        #self.log ( "max_channel = %d" % max_channel )
        #self.log ( "min_channel = %d" % min_channel )

        self.log ( "info: create_unwrapped_phase_map_array() took %ds." % ( time ( ) - i_start ) )

    def get_array ( self ):
        """
        Returns the raw data array (same as the input).
        """
        return self.__array

    def get_borders_to_center_distances ( self ):
        """
        Returns the array containing the distances from each border pixel to the tuned center of the array.
        """
        return self.__fa_borders_to_center_distances

    def get_continuum_array ( self ):
        """
        Returns the continuum array.
        """
        return self.continuum_array

    def get_parabolic_Polynomial2D_model ( self ):
        """
        Returns a parabolic model of the data.
        """
        return self.__ffa_parabolic_model_Polynomial2D

    def get_parabolic_Polynomial2D_coefficients ( self ):
        return self.__parabolic_coefficients

    def get_wrapped_phase_map_array ( self ):
        """
        Returns the phase map.
        """
        return self.wrapped_phase_map_array

    def get_binary_noise_array ( self ):
        """
        Returns the binary noise.
        """
        return self.binary_noise_array

    def get_ring_borders_array ( self ):
        """
        Returns the ring borders.
        """
        return self.ring_borders_array

    def get_order_array ( self ):
        """
        Return the relative FSR map.
        """
        return self.order_array

    def get_unwrapped_phase_map_array ( self ):
        return self.unwrapped_phase_map

    def verify_parabolic_model ( self ):
        self.log ( "info: Ratio between 2nd degree coefficients is: %f" % ( self.__parabolic_coefficients [ 'x2y0' ] / 
                                                                            self.__parabolic_coefficients [ 'x0y2' ] ) )

def create_max_channel_map ( self, array = numpy.ndarray ):
    """
    Uses numpy.argmax to return the 2D array with the maxima along the depth of a 3D cube.
    Notice that numpy currently returns the index of the first maximum if there are several maxima.
    """
    return numpy.argmax ( array, axis = 0 )
