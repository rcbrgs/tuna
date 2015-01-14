from math import floor, sqrt
import numpy
from file_format import adhoc, file_reader, fits
from gui import widget_viewer_2d
from .orders import orders

class high_resolution_Fabry_Perot_phase_map_creation ( object ):
    def __init__ ( self, file_object = file_reader.file_reader, file_name = str, log = None, bad_neighbours_threshold = 7, channel_threshold = 1, *args, **kwargs ):
        super ( high_resolution_Fabry_Perot_phase_map_creation, self ).__init__ ( *args, **kwargs )
        if log:
            self.log = log
        else:
            self.log = print
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

        self.__image_ndarray = current_file.get_image_ndarray ( )
        
        if self.__image_ndarray.ndim == 3:
            self.log ( "Creating maximum channel per pixel image." )
            self.max_channel_map = numpy.argmax ( self.__image_ndarray, axis=0 )
        else:
            self.log ( "Image does not have 3 dimensions, aborting." )
            return

        self.create_binary_noise_map ( bad_neighbours_threshold = bad_neighbours_threshold, channel_threshold = channel_threshold )
        self.create_ring_borders_map ( )
        self.create_regions_map ( )
        self.create_order_map ( )
        self.create_unwrapped_phases_map ( )

    def get_image_ndarray ( self ):
        return self.__image_ndarray

    def get_max_channel_map ( self ):
        return self.max_channel_map

    def get_binary_noise_map ( self ):
        return self.binary_noise_map

    def create_binary_noise_map ( self, bad_neighbours_threshold = 7, channel_threshold = 1 ):
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
        self.log ( "Producing binary noise map." )
        map = numpy.zeros ( shape = self.max_channel_map.shape )
        max_channel = numpy.amax ( self.max_channel_map )
        for x in range ( self.max_channel_map.shape[0] ):
            for y in range ( self.max_channel_map.shape[1] ):
                this_channel = self.max_channel_map[x][y]
                neighbours = self.get_neighbours ( ( x, y ), self.max_channel_map )
                bad_results = 0
                for neighbour in neighbours:
                    result = ( self.max_channel_map[neighbour[0]][neighbour[1]] - this_channel )
                    other_result = this_channel + ( max_channel - self.max_channel_map[neighbour[0]][neighbour[1]] )
                    if result > other_result:
                        result = other_result
                    if result > channel_threshold:
                        bad_results += 1
                if ( bad_results > bad_neighbours_threshold ):
                    map[x][y] = 1.0

        self.binary_noise_map = map

    def get_neighbours ( self, position = ( int, int ), ndarray = numpy.ndarray ):
        result = []
        x = position[0]
        y = position[1]
        possible_neighbours = [ ( x-1, y+1 ), ( x, y+1 ), ( x+1, y+1 ),
                                ( x-1, y   ),             ( x+1, y   ),
                                ( x-1, y-1 ), ( x, y-1 ), ( x+1, y-1 ) ]

        def is_valid_position ( position = ( int, int ), ndarray = numpy.ndarray ):
            if ( position[0] >= 0 and 
                 position[0] < ndarray.shape[0] ):
                if position[1] >= 0 and position[1] < ndarray.shape[1]:
                    return True
            return False

        for possibility in possible_neighbours:
            if is_valid_position ( position = possibility, ndarray = ndarray ):
                result.append ( possibility )
                
        return result

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
        #self.log ( order_object.get_array ( ) )
        #self.order_map = numpy.copy ( order_object.get_array ( ) )

    def create_order_map_old ( self ):
        self.log ( "Producing order map." )
        self.order_map = numpy.zeros ( shape = self.regions_map.shape )
        max_x = self.regions_map.shape[0]
        max_y = self.regions_map.shape[1]

        pixel_count = 0
        center_x = 0
        center_y = 0
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( self.ring_borders_map[x][y] == 1 ):
                    pixel_count += 1
                    center_x += x
                    center_y += y
        center_x /= int ( pixel_count )
        center_y /= int ( pixel_count )
        center_color = self.regions_map[center_x][center_y] 
        self.log ( "Center of symmetric rings possibly near (%d, %d)." % ( center_x, center_y ) )
        self.log ( "Center in region of color %d." % center_color )

        colors = [ ]
        connections = [ ]
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( self.regions_map[x][y] not in colors ):
                    colors.append ( self.regions_map[x][y] )
                if ( self.ring_borders_map[x][y] == 1 ):
                    neighbourhood = self.get_neighbours ( position = ( x, y ), ndarray = self.regions_map )
                    relationship = []
                    for neighbour in neighbourhood:
                        if self.regions_map[neighbour[0]][neighbour[1]] > 1:
                            if self.regions_map[neighbour[0]][neighbour[1]] not in relationship:
                                relationship.append ( self.regions_map[neighbour[0]][neighbour[1]] )
                    if len ( relationship ) == 2:
                        if relationship not in connections:
                            if [ relationship[1], relationship[0] ] not in connections:
                                connections.append ( relationship )
        print ( "Neighbourhood connections: ", connections )
        colors.remove ( 0.0 )
        print ( "Region colors: %s." % colors )

        region_order = { 0 : [ center_color ] }
        order = 0

        while connections != []:
        #for Z in range ( 10 ):
            while order in region_order:
                order += 1
            for color in colors:
                for connectee in region_order[order-1]:
                    if ( [color, connectee] in connections ):
                        connections.remove ( [color, connectee] )
                        if ( order in region_order ):
                            region_order[order].append ( color )
                        else:
                            region_order[order] = [ color ]
                    if ( [connectee, color] in connections ):
                        connections.remove ( [connectee, color] )
                        if ( order in region_order ):
                            region_order[order].append ( color )
                        else:
                            region_order[order] = [ color ]
            self.log ( "region_order = %s." % region_order )

        for x in range ( max_x ):
            for y in range ( max_y ):
                color = self.regions_map[x][y]
                for order_key in region_order.keys ( ):
                    if color in region_order[order_key]:
                        self.order_map[x][y] = order_key
                        break

        # Rings borders should get the value of its largest neighbouring region.
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.ring_borders_map[x][y] == 1:
                    order = 0
                    for neighbour in self.get_neighbours ( position = ( x, y ), ndarray = self.order_map ):
                        if self.order_map[neighbour[0]][neighbour[1]] > order:
                            order = self.order_map[neighbour[0]][neighbour[1]]
                    self.order_map[x][y] = order

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

