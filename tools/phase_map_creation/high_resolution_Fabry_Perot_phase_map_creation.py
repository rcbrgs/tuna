from math import floor
import numpy
from file_format import adhoc, file_reader, fits
from gui import widget_viewer_2d

class high_resolution_Fabry_Perot_phase_map_creation ( object ):
    def __init__ ( self, file_object = file_reader.file_reader, file_name = str, log = None, *args, **kwargs ):
        super ( high_resolution_Fabry_Perot_phase_map_creation, self ).__init__ ( *args, **kwargs )
        if log:
            self.log = log
        else:
            self.log = print

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

        self.image_ndarray = current_file.get_image_ndarray ( )
        
        if self.image_ndarray.ndim == 3:
            self.max_intensity = numpy.amax   ( self.image_ndarray, axis=0 )
            self.max_slice     = numpy.argmax ( self.image_ndarray, axis=0 )
        else:
            self.log ( "Image does not have 3 dimensions, aborting." )
            return

        self.neighbours_to_consider = numpy.zeros ( shape = ( self.image_ndarray.shape[1], self.image_ndarray.shape[2] ) )
        self.phase_map_ndarray = numpy.ndarray ( shape = ( self.image_ndarray.shape[1], self.image_ndarray.shape[2] ) )
        self.log ( "Extracting phase map image from phase map table." )
        for x in range ( self.image_ndarray.shape[1] ):
            for y in range ( self.image_ndarray.shape[2] ):
                self.phase_map_ndarray[x][y] = self.max_slice[x][y]
        self.unwrap_phases ( )

    def get_image_ndarray ( self ):
        return self.phase_map_ndarray

    def get_binary_noise_map ( self ):
        """
        This method will be applied to each pixel; it is at channel C.
        All neighbours should be either in the same channel,
        in the channel C +- 1, or, if C = 0 or C = max, the neighbours
        could be at max or 0.
        Pixels that do not conform to this are noisy and get value 1.
        Normal pixels get value 0 and this produces a binary noise map.
        """
        self.log ( "Producing binary noise map." )
        map = numpy.zeros ( shape = self.phase_map_ndarray.shape )
        max_channel = numpy.amax ( self.phase_map_ndarray )
        for x in range ( self.phase_map_ndarray.shape[0] ):
            for y in range ( self.phase_map_ndarray.shape[1] ):
                this_channel = self.phase_map_ndarray[x][y]
                good_results = []
                if this_channel == 0:
                    good_results.append ( 0 )
                    good_results.append ( 1 )
                    good_results.append ( max_channel )
                elif this_channel == max_channel:
                    good_results.append ( max_channel )
                    good_results.append ( 0 )
                    good_results.append ( max_channel - 1 )
                else:
                    good_results.append ( this_channel )
                    good_results.append ( this_channel + 1 )
                    good_results.append ( this_channel - 1 )
                neighbours = self.get_neighbours ( ( x, y ), self.phase_map_ndarray )                    
                for neighbour in neighbours:
                    if self.phase_map_ndarray[neighbour[0]][neighbour[1]] not in good_results:
                        map[x][y] = 1.0
                        break
        return map                    

    def unwrap_phases ( self ):
        self.log ( "Unwrapping the phases." )
        max_x = self.image_ndarray.shape[1]
        max_y = self.image_ndarray.shape[2]
        max_channel = numpy.amax ( self.max_slice )
        min_channel = numpy.amin ( self.max_slice )
        self.log ( "max_x = %d" % max_x )
        self.log ( "max_y = %d" % max_y )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

        test_mat = numpy.ndarray ( shape = ( self.image_ndarray.shape[1], 3 ) )
        test_row = 152
        if test_row != -1:
            #print ( self.max_slice[0:-1][152] )
            for x in range ( max_x ):
                test_mat [x][0] = self.max_slice[x][test_row]

        binary_noise_mask = self.get_binary_noise_map ( )
        max_zeroes = 0
        order_multipliers = numpy.zeros ( shape = ( max_y, max_x ) )
        last_printed = 0
        for y in range ( max_y ):
            percentage_done = ( int ) ( 100 * y / max_y )
            if not last_printed == percentage_done:
                #self.log ( "Unwrapping phase %2d" % percentage_done + '%' )
                last_printed = percentage_done

            zeroes = 0
            for x in range ( max_x ):
                if binary_noise_mask[x][y] == 0:
                    if self.max_slice[x][y] == 0.0:
                        if x-1 > 0:
                            if self.max_slice[x-1][y] == max_channel:
                                order_multipliers[y][x] = 1
                                zeroes += 1
                        if x+1 < max_x:
                            if self.max_slice[x+1][y] == max_channel:
                                order_multipliers[y][x+1] = -1
                                zeroes += 1
            if zeroes > max_zeroes: 
                max_zeroes = zeroes

        for y in range ( max_y ):
            zeroes = max_zeroes
            multipliers = numpy.zeros ( shape = ( max_x ) )
            for x in range ( max_x ):
                if binary_noise_mask[x][y] == 0:
                    if order_multipliers[y][x] == 1:
                        zeroes += 2
                    if order_multipliers[y][x] == -1:
                        zeroes -= 2
                multipliers[x] = floor ( zeroes / 2 )

            if y == test_row:
                #print ( multipliers )
                for x2 in range ( max_x ):
                    test_mat [x2][1] = multipliers[x2]
        

            for x in range ( max_x ):
                #self.max_slice[x][y] += max_channel * multipliers[x]
                self.max_slice[x][y] = multipliers[x]

        if test_row != -1:
            #print ( self.max_slice[0:-1][152] )
            for x in range ( max_x ):
                test_mat [x][2] = self.max_slice[x][test_row]

        print_str = ""
        for x in range ( max_x ):
            print_str += str ( "(%3d,%3d,%3d)" % ( test_mat[x][0], test_mat[x][1], test_mat[x][2] ) )
        print ( print_str )

        self.phase_map_ndarray = self.max_slice

        max_channel = numpy.amax ( self.max_slice )
        min_channel = numpy.amin ( self.max_slice )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

    def get_neighbours ( self, position = ( int, int ), ndarray = numpy.ndarray ):
        #print ( "get_neighbours", position )
        result = []
        x = position[0]
        y = position[1]
        possible_neighbours = [ ( x-1, y+1 ), ( x, y+1 ), ( x+1, y+1 ),
                                ( x-1, y   ),             ( x+1, y   ),
                                ( x-1, y-1 ), ( x, y-1 ), ( x+1, y-1 ) ]

        def is_valid_position ( position = ( int, int ), ndarray = numpy.ndarray ):
            #print ( "is_valid_position", position )
            #print ( ndarray.shape )
            if ( position[0] > 0 and 
                 position[0] < ndarray.shape[0] ):
                if position[1] > 0 and position[1] < ndarray.shape[1]:
                    return True
            return False

        for possibility in possible_neighbours:
            if is_valid_position ( possibility, ndarray ):
                result.append ( possibility )
                
        return result
