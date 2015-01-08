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

        index_intensity = 0
        index_slice = 1
        if self.image_ndarray.ndim == 3:
            self.max_slice = numpy.ndarray ( shape = ( 2, self.image_ndarray.shape[1], 
                                                          self.image_ndarray.shape[2] ) )
            max_x = self.image_ndarray.shape[1]
            last_printed = 0
            for x in range ( self.image_ndarray.shape[1] ):
                percentage_done = int ( 100 * x / max_x )
                if not percentage_done == last_printed:
                    self.log ( "Finding spectral peak %2d" % percentage_done + '%' )
                    last_printed = percentage_done
                for y in range ( self.image_ndarray.shape[2] ):
                    for slice in range ( self.image_ndarray.shape[0] ):
                        if  self.max_slice[index_intensity][x][y] < self.image_ndarray[slice][x][y]:
                            self.max_slice[index_intensity][x][y] = self.image_ndarray[slice][x][y]
                            self.max_slice[index_slice][x][y] = slice              
        else:
            self.log ( "Image does not have 3 dimensions, aborting." )
            return

        self.neighbours_to_consider = numpy.zeros ( shape = ( self.image_ndarray.shape[1], self.image_ndarray.shape[2] ) )
        self.unwrap_phases3 ( )
        self.phase_map_ndarray = numpy.ndarray ( shape = ( self.image_ndarray.shape[1], self.image_ndarray.shape[2] ) )
        
        self.log ( "Extracting phase map image from phase map table." )
        for x in range ( self.image_ndarray.shape[1] ):
            for y in range ( self.image_ndarray.shape[2] ):
                self.phase_map_ndarray[x][y] = self.max_slice[index_slice][x][y]

    def get_image_ndarray ( self ):
        return self.phase_map_ndarray

    def unwrap_phases3 ( self ):
        self.log ( "Unwrapping the phases." )
        max_x = self.image_ndarray.shape[1]
        max_y = self.image_ndarray.shape[2]
        max_channel = numpy.amax ( self.max_slice[1] )
        min_channel = numpy.amin ( self.max_slice[1] )
        self.log ( "max_x = %d" % max_x )
        self.log ( "max_y = %d" % max_y )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

        max_zeroes = 0
        order_multipliers = numpy.zeros ( shape = ( max_y, max_x ) )
        last_printed = 0
        for y in range ( max_y ):
            percentage_done = (int ) ( 100 * y / max_y )
            if not last_printed == percentage_done:
                self.log ( "Unwrapping phase %2d" % percentage_done + '%' )
                last_printed = percentage_done

            zeroes = 0
            for x in range ( max_x ):
                if self.max_slice[1][x][y] == 0.0:
                    if x-1 > 0:
                        if self.max_slice[1][x-1][y] == max_channel:
                            order_multipliers[y][x] = 1
                            zeroes += 1
                    if x+1 < max_x:
                        if self.max_slice[1][x+1][y] == max_channel:
                            order_multipliers[y][x] = -1
                            zeroes += 1
            if zeroes > max_zeroes: 
                max_zeroes = zeroes

        for y in range ( max_y ):
            zeroes = max_zeroes
            multipliers = numpy.zeros ( shape = ( max_x ) )
            for x in range ( max_x ):
                if order_multipliers[y][x] == 1:
                    zeroes += 2
                if order_multipliers[y][x] == -1:
                    zeroes -= 2
                multipliers[x] = floor ( zeroes / 2 )

            for x in range ( max_x ):
                self.max_slice[1][x][y] += max_channel * multipliers[x]


        max_channel = numpy.amax ( self.max_slice[1] )
        min_channel = numpy.amin ( self.max_slice[1] )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )


    def unwrap_phases2 ( self ):
        self.log ( "Unwrapping the phases." )
        max_x = self.image_ndarray.shape[1]
        max_y = self.image_ndarray.shape[2]
        max_channel = numpy.amax ( self.max_slice[1] )
        min_channel = numpy.amin ( self.max_slice[1] )
        self.log ( "max_x = %d" % max_x )
        self.log ( "max_y = %d" % max_y )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

        test_line=256
        row = []
        for item in range ( max_x ):
            row.append ( self.max_slice[1][item][test_line] )
        print ( row )

        last_printed = 0
        for y in range ( max_y ):
            percentage_done = (int ) ( 100 * y / max_y )
            if not last_printed == percentage_done:
                self.log ( "Unwrapping phase %2d" % percentage_done + '%' )
                last_printed = percentage_done

            order_multipliers = numpy.zeros ( shape = ( max_x ) )
            zeroes = 0
            for x in range ( max_x ):
                if self.max_slice[1][x][y] == 0.0:
                    if x-1 > 0:
                        if self.max_slice[1][x-1][y] == max_channel:
                            order_multipliers[x] = 1
                            zeroes += 1
                    if x+1 < max_x:
                        if self.max_slice[1][x+1][y] == max_channel:
                            order_multipliers[x] = -1
                            zeroes += 1
                        
            if y == test_line:
                print ( "line ", y, " has ", zeroes, " zeroes." )

            multipliers = numpy.zeros ( shape = ( max_x ) )
            for x in range ( max_x ):
                if order_multipliers[x] == 1:
                    zeroes += 2
                if order_multipliers[x] == -1:
                    zeroes -= 2
                multipliers[x] = floor ( zeroes / 2 )
                    
                        
            #multipliers = numpy.zeros ( shape = ( max_x ) )
            #climbing = True
            #for x in range ( max_x ):
            #    if climbing == True:
            #        if order_multipliers[x] == 1:
            #            zeroes -= 2
            #        if zeroes == 0:
            #            climbing = False
            #    else:
            #        if order_multipliers[x] == 1:
            #            zeroes += 2
            #    multipliers[x] = zeroes / 2

            if y == test_line:
                print ( multipliers )
            for x in range ( max_x  ):
                self.max_slice[1][x][y] += max_channel * multipliers[x]

        max_channel = numpy.amax ( self.max_slice[1] )
        min_channel = numpy.amin ( self.max_slice[1] )
        self.log ( "max_channel = %d" % max_channel )
        self.log ( "min_channel = %d" % min_channel )

        row = []
        for item in range ( max_x ):
            row.append ( self.max_slice[1][item][test_line] )
        print ( row )

    def unwrap_phases ( self ):
        """
        1. Let A and B be zero-filled auxiliary arrays.
        2. Let P = (0,0).
        3. For P and every neighbour of P that is not peaking at channel 0, 
           we attribute the value 1 in B.
        4. For every other "internal" pixel, we subtract one from its position in A.
        5. Select any pixel that has 0 in its position in B as the new P.
           If there are none, goto step 6. Otherwise return to step 3.
        (At this point, A must be an array containing concentric rings of
        negative integers, corresponding to the inverse of their "distance"
        from the highest order in the sample).
        6. Let max_order = min (A) * (-1)
        7. For every element in A, add max_order.
        (At this point, A must be an array containing concentric rings of
        non-negative integers, corresponding to their "distance" from the 
        highest order in the sample).
        8. For every element in self.max_slice, add the value in the same
        position in A.
        """
        self.log ( "Unwrapping the phases." )
        max_x = self.image_ndarray.shape[1]
        max_y = self.image_ndarray.shape[2]
        self.log ( "max_x = %d" % max_x )
        self.log ( "max_y = %d" % max_y )
        A = numpy.ndarray ( shape = ( max_x, max_y ) )
        self.processed = numpy.ndarray ( shape = ( max_x, max_y ) )
        for x in range ( max_x ):
            for y in range ( max_y ):
                A[x][y] = 0
                self.processed[x][y] = 0
        
        position = ( 0, 0 )

        while position is not None:
            print ( "position = ", position )
            neighbourhood = self.get_neighbours ( position )

            for x in range ( max_x ):
                for y in range ( max_y ):
                    if ( x, y ) in neighbourhood:
                        print ( "(", x, ", ", y, ") is in neighbourhood." )
                        self.processed[x][y] = 1
                    else:
                        if self.processed[x][y] == 0:
                            A[x][y] -= 1
            
            position = None
            for x in range ( max_x ):
                for y in range ( max_y ):
                    if self.processed[x][y] == 0:
                        position = ( x, y )
                        break
                if position is not None:
                    break

        max_order = numpy.amin ( A ) * ( -1 )
        print ( "max_order = ", max_order )

    def position_has_been_considered ( self, position = ( int, int ) ):
        if self.neighbours_to_consider[position[0]][position[1]] == 0:
            return False
        return True

    def get_neighbours ( self, position = ( int, int ) ):
        print ( "get_neighbours ( position = ", position )
        result = []
        x = position[0]
        y = position[1]
        possible_neighbours = [ ( x-1, y+1 ), ( x, y+1 ), ( x+1, y+1 ),
                                ( x-1, y   ),             ( x+1, y   ),
                                ( x-1, y-1 ), ( x, y-1 ), ( x+1, y-1 ) ]

        def is_valid_position ( position = ( int, int ) ):
            if position[0] > 0 and position[0] < self.max_slice.shape[1]:
                if position[1] > 0 and position[1] < self.max_slice.shape[2]:
                    return True
            return False

        result.append ( position )
        self.neighbours_to_consider [position[0]][position[1]] = 1

        for possibility in possible_neighbours:
            if is_valid_position ( possibility ):
                if self.position_has_been_considered ( possibility ):
                    break
                difference = self.max_slice[1][possibility[0]][possibility[1]] - self.max_slice[1][position[0]][position[1]] 
                if difference ** 2 == 1:
                    result.append ( self.get_neighbours ( ( possibility[0], possibility[1] ) ) )
                
        return result
