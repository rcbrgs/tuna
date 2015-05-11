import logging
from math import sqrt
import numpy
from time import time
#from tuna.tools.get_pixel_neighbours import get_pixel_neighbours
import tuna

class ring_borders ( object ):
    def __init__ ( self, array = None, center = ( int, int ), noise_array = None ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )
        super ( ring_borders, self ).__init__ ( )

        self.__array = array
        self.__borders_to_center_distances = None
        self.__center = center
        self.__noise_array = noise_array
        self.__synthetic_borders = None

    def create_borders_to_center_distances ( self ):
        """
        Supposing there is an array for the borders, and the center has been found, produce an array with the distances from each border pixel to the center.
        """
        borders_to_center_distances = self.__ring_borders_map - self.__noise_array
        self.log.info ( "distances array 0% created." )
        last_percentage_logged = 0
        for row in range ( borders_to_center_distances.shape[0] ):
            percentage = 10 * int ( row / borders_to_center_distances.shape [ 0 ] * 10 )
            if percentage > last_percentage_logged:
                self.log.info ( "distances array %d%% created." % percentage )
                last_percentage_logged = percentage
            for col in range ( borders_to_center_distances.shape[1] ):
                if borders_to_center_distances[row][col] == 1:
                    borders_to_center_distances[row][col] = sqrt ( ( row - self.__center[0] ) ** 2 +
                                                                   ( col - self.__center[1] ) ** 2 )
        self.log.info ( "distances array 100%% created." )

        self.__borders_to_center_distances = borders_to_center_distances

    def create_map_from_barycenter_array ( self ):
        #self.log ( "Producing ring borders map." )
        ring_borders_map = numpy.zeros ( shape = self.__array.shape )
        max_x = self.__array.shape[0]
        max_y = self.__array.shape[1]
        max_channel = numpy.amax ( self.__array )
        threshold = max_channel / 2
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.__noise_array[x][y] == 1:
                    ring_borders_map[x][y] = 1
                    continue
                neighbours = tuna.tools.get_pixel_neighbours ( ( x, y ), ring_borders_map )
                for neighbour in neighbours:
                    if self.__noise_array[neighbour[0]][neighbour[1]] == 0:
                        distance = self.__array[x][y] - self.__array[neighbour[0]][neighbour[1]]
                        if distance > threshold:
                            ring_borders_map[x][y] = 1
                            break

        self.__ring_borders_map = ring_borders_map

    def create_map_from_max_channel_array ( self ):
        #self.log ( "Producing ring borders map." )
        ring_borders_map = numpy.zeros ( shape = self.__array.shape )
        max_x = self.__array.shape[0]
        max_y = self.__array.shape[1]
        max_channel = numpy.amax ( self.__array )
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.__noise_array[x][y] == 0:
                    if self.__array[x][y] == 0.0:
                        neighbours = tuna.tools.get_pixel_neighbours ( ( x, y ), ring_borders_map )
                        for neighbour in neighbours:
                            if self.__array[neighbour[0]][neighbour[1]] == max_channel:
                                ring_borders_map[x][y] = 1.0
                                break
        self.__ring_borders_map = ring_borders_map

    def create_synthetic_borders ( self ):
        if self.__borders_to_center_distances == None:
            self.create_borders_to_center_distances ( )
        array = numpy.zeros ( shape = self.__borders_to_center_distances.shape, dtype = numpy.int8 )
        # collect all distinct radii values in a list
        distinct_radii = [ ]
        for row in range ( array.shape[0] ):
            for col in range ( array.shape[1] ):
                element = int ( self.__borders_to_center_distances[row][col] )
                if element != 0:
                    if element not in distinct_radii:
                        distinct_radii.append ( element )
        sorted_radii = sorted ( distinct_radii )
        #print ( sorted_radii )
        # Collapse sequential values
        #collapsed_radii = [ sorted_radii[0] ]
        #for element in range ( 1, len ( sorted_radii ) ):
        #    if ( sorted_radii[element] != sorted_radii[element - 1] + 1 ):
        #        collapsed_radii.append ( sorted_radii[element] )

        # Produce an array where pixels distant any radii from the center have a value of 1.
        for row in range ( array.shape[0] ):
            for col in range ( array.shape[1] ):
                distance = sqrt ( ( self.__tuned_center[0] - row ) ** 2 +
                                    ( self.__tuned_center[1] - col ) ** 2 )
                #for radius in collapsed_radii:
                for radius in sorted_radii:
                    # These values were chosen so that the border will necessarily fall within a "band" with halfwidth of 2^1/2 pixels.
                    if ( ( distance > radius - 1.5 ) and
                         ( distance < radius + 1.5 ) ):
                        array[row][col] = radius
        #print ( array[200] )
        self.__synthetic_borders = array

    def get_borders_to_center_distances ( self ):
        if self.__borders_to_center_distances == None:
            self.create_borders_to_center_distances ( )
        return self.__borders_to_center_distances

    def get_map ( self ):
        return self.__ring_borders_map

    def get_synthetic_borders ( self ):
        if self.__synthetic_borders == None:
            self.create_synthetic_borders ( )
        return self.__synthetic_borders

def create_ring_borders_map ( array = None, center = ( int, int ), noise_array = None ):
    start = time ( )

    log = loggging.getLogger ( __name__ )

    ring_borders_object = ring_borders ( array = array, center = center, noise_array = noise_array )
    ring_borders_object.create_map_from_barycenter_array ( )
    ring_borders_object.create_synthetic_borders ( )

    log.info ( "create_ring_borders_map() took %ds." % ( time ( ) - start ) )
    return ring_borders_object.get_synthetic_borders ( )

def create_borders_to_center_distances ( array = None, center = ( int, int ), noise_array = None ):
    start = time ( )

    log = logging.getLogger ( __name__ )
    ring_borders_object = ring_borders ( array = array, center = center, noise_array = noise_array )
    ring_borders_object.create_map_from_barycenter_array ( )
    result = ring_borders_object.get_borders_to_center_distances ( )
    result_can = tuna.io.can ( array = result )

    log.info ( "create_borders_to_center_distances() took %ds." % ( time ( ) - start ) )
    return result_can
