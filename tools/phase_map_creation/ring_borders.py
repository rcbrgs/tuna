import numpy
from tools.get_pixel_neighbours import get_pixel_neighbours

class ring_borders ( object ):
    def __init__ ( self, array = None, log = print, noise_array = None ):
        super ( ring_borders, self ).__init__ ( )
        self.__array = array
        self.__noise_array = noise_array
        self.log = log

    def create_map_from_barycenter_array ( self ):
        self.log ( "Producing ring borders map." )
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
                neighbours = get_pixel_neighbours ( ( x, y ), ring_borders_map )
                for neighbour in neighbours:
                    if self.__noise_array[neighbour[0]][neighbour[1]] == 0:
                        distance = self.__array[x][y] - self.__array[neighbour[0]][neighbour[1]]
                        if distance > threshold:
                            ring_borders_map[x][y] = 1
                            break

        self.__ring_borders_map = ring_borders_map

    def create_map_from_max_channel_array ( self ):
        self.log ( "Producing ring borders map." )
        ring_borders_map = numpy.zeros ( shape = self.__array.shape )
        max_x = self.__array.shape[0]
        max_y = self.__array.shape[1]
        max_channel = numpy.amax ( self.__array )
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.__noise_array[x][y] == 0:
                    if self.__array[x][y] == 0.0:
                        neighbours = get_pixel_neighbours ( ( x, y ), ring_borders_map )
                        for neighbour in neighbours:
                            if self.__array[neighbour[0]][neighbour[1]] == max_channel:
                                ring_borders_map[x][y] = 1.0
                                break
        self.__ring_borders_map = ring_borders_map

    def get_map ( self ):
        return self.__ring_borders_map

def create_ring_borders_map ( log = print, array = None, noise_array = None ):
    ring_borders_object = ring_borders ( log = log, array = array, noise_array = noise_array )
    ring_borders_object.create_map_from_barycenter_array ( )
    return ring_borders_object.get_map ( )
