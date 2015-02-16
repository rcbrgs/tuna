#from .concentric_rings_model import find_concentric_rings
from math import floor, sqrt
import numpy
from file_format import adhoc, file_reader, fits
from .find_image_center_by_symmetry import find_image_center_by_symmetry
from gui import widget_viewer_2d
from .noise import create_noise_array
from .orders import orders
from .ring_borders import create_ring_borders_map, create_borders_to_center_distances
from tools.get_pixel_neighbours import get_pixel_neighbours
from .spectrum import create_continuum_array
from time import time

def create_max_channel_map ( self, array = numpy.ndarray ):
    """
    Uses numpy.argmax to return the 2D array with the maxima along the depth of a 3D cube.
    Notice that numpy currently returns the index of the first maximum if there are several maxima.
    """
    return numpy.argmax ( array, axis = 0 )

class high_resolution_Fabry_Perot_phase_map_creation ( object ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.
    Intermediary products are the binary noise, the ring borders, the regions and orders maps.
    """
    def __init__ ( self, 
                   array = numpy.ndarray,
                   bad_neighbours_threshold = 7, 
                   channel_threshold = 1, 
                   log = print, 
                   noise_mask_radius = 0,
                   wrapped_phase_map_algorithm = create_max_channel_map, 
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
        super ( high_resolution_Fabry_Perot_phase_map_creation, self ).__init__ ( *args, **kwargs )
        self.log = log

        self.__array = array
        
        if self.__array.ndim != 3:
            self.log ( "Image does not have 3 dimensions, aborting." )
            return

        self.continuum_array = create_continuum_array ( array = array )

        self.filtered_array = numpy.ndarray ( shape = array.shape )
        for dep in range ( array.shape[0] ):
            self.filtered_array[dep,:,:] = array[dep,:,:] - self.continuum_array

        self.wrapped_phase_map_array = wrapped_phase_map_algorithm ( array = self.filtered_array )

        self.__iit_center = find_image_center_by_symmetry ( ia_data = self.wrapped_phase_map_array )

        self.binary_noise_array = create_noise_array ( bad_neighbours_threshold = bad_neighbours_threshold, 
                                                       channel_threshold = channel_threshold, 
                                                       array = self.wrapped_phase_map_array, 
                                                       noise_mask_radius = noise_mask_radius )

        ia_ring_borders_array = create_ring_borders_map ( log = self.log, 
                                                          array = self.wrapped_phase_map_array,
                                                          iit_center = self.__iit_center,
                                                          noise_array = self.binary_noise_array )
        self.ring_borders_array = ia_ring_borders_array.astype ( float )

        
        self.__fa_borders_to_center_distances = create_borders_to_center_distances ( log = self.log, 
                                                                                     array = self.wrapped_phase_map_array,
                                                                                     iit_center = self.__iit_center,
                                                                                     noise_array = self.binary_noise_array )

        #self.ring_borders_array = self.__borders_to_center_distances
        #print ( self.ring_borders_array[200] )

        self.create_regions_array ( )
        self.create_order_array ( )
        self.create_unwrapped_phase_map_array ( )

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
        #print ( self.ring_borders_array[200] )
        return self.ring_borders_array

    def create_regions_array ( self ):
        """
        Creates a 2D numpy.ndarray where each pixel will have a value of -1 if it is noise; 0 if it is in a border; and some multiple of 10 otherwise.
        The map is created by selecting a non-
        """
        i_start = time ( )
        self.log ( "create_regions_array", end = '' )

        self.regions_array = numpy.zeros ( shape = self.ring_borders_array.shape )
        max_x = self.regions_array.shape[0]
        max_y = self.regions_array.shape[1]
        color = 0

        #self.regions_array = -1 * self.binary_noise_array

        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( self.regions_array[x][y] == 0 ):
                    if ( self.ring_borders_array[x][y] == 0 ):
                        possibly_in_region = [ ( x, y ) ]
                        color += 10
                        if ( color > 1000 ):
                            self.log ( "More than a 100 colors? There must be a mistake. Aborting." )
                            return
                        #self.log ( "Filling region %d." % ( color / 10 ) )
                        while ( possibly_in_region != [ ] ):
                            testing = possibly_in_region.pop ( )
                            if self.regions_array[testing[0]][testing[1]] == 0:
                                self.regions_array[testing[0]][testing[1]] = color
                                neighbourhood = get_pixel_neighbours ( position = ( testing[0], testing[1] ), array = self.regions_array )
                                for neighbour in neighbourhood:
                                    if self.ring_borders_array[neighbour[0]][neighbour[1]] == 0:
                                        #if self.binary_noise_array[neighbour[0]][neighbour[1]] == 0:
                                        #    possibly_in_region.append ( neighbour )
                                        possibly_in_region.append ( neighbour )

        # Coloring borders so that pixels change region when they wrap around the FSR.
        ia_nonexplored_borders = numpy.copy ( self.ring_borders_array )
        while ( numpy.sum ( ia_nonexplored_borders ) > 0 ):
            for x in range ( max_x ):
                for y in range ( max_y ):
                    if ( ia_nonexplored_borders[x][y] > 0 ):
                        neighbourhood = get_pixel_neighbours ( position = ( x, y ), array = self.regions_array )
                        il_possible_colors = [ ]
                        for neighbour in neighbourhood:
                            if ia_nonexplored_borders[neighbour[0]][neighbour[1]] == 0:
                                il_possible_colors.append ( self.regions_array[neighbour[0]][neighbour[1]] )
                        if il_possible_colors != [ ]:
                            ia_nonexplored_borders[x][y] = 0
                            self.borders_array = min ( il_possible_colors )                        
                
        self.log ( " %ds." % ( time ( ) - i_start ) )

    def get_regions_array ( self ):
        return self.regions_array

    def create_order_array ( self ):
        orders_algorithm = orders ( fa_borders_to_center_distances = self.__fa_borders_to_center_distances, iit_center = self.__iit_center, regions = self.regions_array, ring_borders = self.ring_borders_array, noise = self.binary_noise_array )
        self.order_array = orders_algorithm.get_orders ( )

    def get_order_array ( self ):
        return self.order_array

    def create_unwrapped_phase_map_array ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        i_start = time ( )
        self.log ( "create_unwrapped_phase_map_array", end='' )

        max_x = self.wrapped_phase_map_array.shape[0]
        max_y = self.wrapped_phase_map_array.shape[1]
        max_channel = numpy.amax ( self.wrapped_phase_map_array )
        min_channel = numpy.amin ( self.wrapped_phase_map_array )
        #self.log ( "max_channel = %d" % max_channel )
        #self.log ( "min_channel = %d" % min_channel )

        self.unwrapped_phase_map = numpy.zeros ( shape = self.wrapped_phase_map_array.shape )

        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.ring_borders_array[x][y] == 0:
                    self.unwrapped_phase_map[x][y] = self.wrapped_phase_map_array[x][y] + max_channel * self.order_array[x][y]
                else:
                    self.unwrapped_phase_map[x][y] = -1 # self.wrapped_phase_map_array[x][y] + max_channel * ( self.order_array[x][y] - 1 )
                    
        max_channel = numpy.amax ( self.unwrapped_phase_map )
        min_channel = numpy.amin ( self.unwrapped_phase_map )
        #self.log ( "After unwrapping:" )
        #self.log ( "max_channel = %d" % max_channel )
        #self.log ( "min_channel = %d" % min_channel )

        self.log ( " %ds." % ( time ( ) - i_start ) )

    def get_unwrapped_phase_map_array ( self ):
        return self.unwrapped_phase_map

def create_high_resolution_phase_map ( array = numpy.ndarray,
                                       wrapped_phase_map_algorithm = create_max_channel_map ):
    high_resolution_Fabry_Perot_phase_map_creation_object = high_resolution_Fabry_Perot_phase_map_creation ( array = array, wrapped_phase_map_algorithm = wrapped_phase_map_algorithm )
    return high_resolution_Fabry_Perot_phase_map_creation_object.get_unwrapped_phase_map ( )
