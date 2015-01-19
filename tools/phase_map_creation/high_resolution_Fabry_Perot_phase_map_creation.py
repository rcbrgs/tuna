from math import floor, sqrt
import numpy
from file_format import adhoc, file_reader, fits
from gui import widget_viewer_2d
from .orders import orders

class high_resolution_Fabry_Perot_phase_map_creation ( object ):
    def __init__ ( self, file_object = file_reader.file_reader, file_name = str, log = print, bad_neighbours_threshold = 7, channel_threshold = 1, *args, **kwargs ):
        super ( high_resolution_Fabry_Perot_phase_map_creation, self ).__init__ ( *args, **kwargs )
        self.log = log
        self.max_channel_map = None

        if file_object == None:
            self.max_channels = None
            fits_file = fits.fits ( file_name = file_name, log = self.log )
            fits_file.read ( )
            if fits_file.is_readable ( ):
                current_file = fits_file
            else:
                adhoc_file = adhoc.adhoc ( file_name = file_name, log = self.log )
                adhoc_file.read ( )
                if adhoc_file.is_readable ( ):
                    current_file = adhoc_file
                else:
                    self.log ( "Unable to open file %s." % file_name )
                    return
        else:
            current_file = file_object

        self.__array = current_file.get_array ( )
        
        if self.__array.ndim == 3:
            self.log ( "Creating maximum channel per pixel image." )
            self.max_channel_map = numpy.argmax ( self.__array, axis=0 )
        else:
            self.log ( "Image does not have 3 dimensions, aborting." )
            return

        self.create_binary_noise_map ( bad_neighbours_threshold = bad_neighbours_threshold, channel_threshold = channel_threshold )
        self.create_ring_borders_map ( )
        self.create_regions_map ( )
        self.create_order_map ( )
        self.create_unwrapped_phases_map ( )

    def get_array ( self ):
        return self.__array

    def get_max_channel_map ( self ):
        return self.max_channel_map

    def get_binary_noise_map ( self ):
        return self.binary_noise_map


    def create_ring_borders_map ( self ):
        self.log ( "Producing ring borders map." )
        self.ring_borders_map = numpy.zeros ( shape = self.max_channel_map.shape )
        max_x = self.max_channel_map.shape[0]
        max_y = self.max_channel_map.shape[1]
        max_channel = numpy.amax ( self.max_channel_map )
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.binary_noise_map[x][y] == 0:
                    if self.max_channel_map[x][y] == 0.0:
                        neighbours = self.get_neighbours ( ( x, y ), self.ring_borders_map )
                        for neighbour in neighbours:
                            if self.max_channel_map[neighbour[0]][neighbour[1]] == max_channel:
                                self.ring_borders_map[x][y] = 1.0
                                break

    def get_ring_borders_map ( self ):
        return self.ring_borders_map

    def create_regions_map ( self ):
        self.log ( "Producing regions map." )
        self.regions_map = numpy.zeros ( shape = self.ring_borders_map.shape )
        max_x = self.regions_map.shape[0]
        max_y = self.regions_map.shape[1]
        color = 0

        self.regions_map += self.binary_noise_map * ( -1 )

        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( self.regions_map[x][y] == 0 ):
                    if ( self.ring_borders_map[x][y] == 0 ):
                        possibly_in_region = [ ( x, y ) ]
                        color += 10
                        if ( color > 1000 ):
                            self.log ( "More than a 100 colors? There must be a mistake. Aborting." )
                            return
                        self.log ( "Filling region %d." % ( color / 10 ) )
                        while ( possibly_in_region != [ ] ):
                            testing = possibly_in_region.pop ( )
                            if self.regions_map[testing[0]][testing[1]] == 0:
                                self.regions_map[testing[0]][testing[1]] = color
                                neighbourhood = self.get_neighbours ( position = ( testing[0], testing[1] ), ndarray = self.regions_map )
                                for neighbour in neighbourhood:
                                    if self.ring_borders_map[neighbour[0]][neighbour[1]] == 0:
                                        if self.binary_noise_map[neighbour[0]][neighbour[1]] == 0:
                                            possibly_in_region.append ( neighbour )

    def get_regions_map ( self ):
        return self.regions_map

    def create_order_map ( self ):
        orders_algorithm = orders ( regions = self.regions_map, ring_borders = self.ring_borders_map )
        self.order_map = orders_algorithm.get_orders ( )

    def get_order_map ( self ):
        return self.order_map

    def create_unwrapped_phases_map ( self ):
        self.log ( "Unwrapping the phases. Before unwrapping:" )
        max_x = self.max_channel_map.shape[0]
        max_y = self.max_channel_map.shape[1]
        max_channel = numpy.amax ( self.max_channel_map )
        min_channel = numpy.amin ( self.max_channel_map )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

        self.unwrapped_phases_map = numpy.zeros ( shape = self.max_channel_map.shape )

        for x in range ( max_x ):
            for y in range ( max_y ):
                self.unwrapped_phases_map[x][y] = self.max_channel_map[x][y] + max_channel * self.order_map[x][y]

        max_channel = numpy.amax ( self.unwrapped_phases_map )
        min_channel = numpy.amin ( self.unwrapped_phases_map )
        self.log ( "After unwrapping:" )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

    def get_unwrapped_phases_map ( self ):
        return self.unwrapped_phases_map


def create_binary_noise_map ( bad_neighbours_threshold = 7, channel_threshold = 1, array = None, log = print ):
    """
    This method will be applied to each pixel; it is at channel C.
    All neighbours should be either in the same channel,
    in the channel C +- 1, or, if C = 0 or C = max, the neighbours
    could be at max or 0.
    Pixels that do not conform to this are noisy and get value 1.
    Normal pixels get value 0 and this produces a binary noise map.
    
    Parameters:
    -----------
    - bad_neighbours_threshold is the number of neighbours with bad 
    values that the algorithm will tolerate. It defaults to 7.
    - channel_threshold is the channel distance that will be tolerated. 
    It defaults to 1.
    """
    log ( "Producing binary noise map." )
    noise_map = numpy.zeros ( shape = array.shape )
    max_channel = numpy.amax ( array )
    for x in range ( array.shape[0] ):
        for y in range ( array.shape[1] ):
            this_channel = array[x][y]
            neighbours = get_neighbours ( ( x, y ), array )
            bad_results = 0
            for neighbour in neighbours:
                result = array[neighbour[0]][neighbour[1]] - this_channel
                other_result = this_channel + ( max_channel - array[neighbour[0]][neighbour[1]] )
                if result > other_result:
                    result = other_result
                if result > channel_threshold:
                    bad_results += 1
            if ( bad_results > bad_neighbours_threshold ):
                noise_map[x][y] = 1.0

    return noise_map

def get_neighbours ( position = ( int, int ), array = None ):
    result = []
    x = position[0]
    y = position[1]
    possible_neighbours = [ ( x-1, y+1 ), ( x, y+1 ), ( x+1, y+1 ),
                            ( x-1, y   ),             ( x+1, y   ),
                            ( x-1, y-1 ), ( x, y-1 ), ( x+1, y-1 ) ]

    def is_valid_position ( position = ( int, int ), array = None ):
        if ( position[0] >= 0 and 
             position[0] < array.shape[0] ):
            if position[1] >= 0 and position[1] < array.shape[1]:
                return True
        return False

    for possibility in possible_neighbours:
        if is_valid_position ( position = possibility, array = array ):
            result.append ( possibility )
                
    return result
