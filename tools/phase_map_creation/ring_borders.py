from math import sqrt
import numpy
from time import time
from tools.get_pixel_neighbours import get_pixel_neighbours

class ring_borders ( object ):
    def __init__ ( self, array = None, iit_center = ( int, int ), log = print, noise_array = None ):
        super ( ring_borders, self ).__init__ ( )
        self.__array = array
        self.__fa_borders_to_center_distances = None
        #self.__il_borders_radii = [ ]
        self.__iit_center = iit_center
        self.__noise_array = noise_array
        self.log = log

    def create_borders_to_center_distances ( self ):
        """
        Supposing there is an array for the borders, and the center has been found, produce an array with the distances from each border pixel to the center.
        """
        fa_borders_to_center_distances = self.__ring_borders_map - self.__noise_array
        for row in range ( fa_borders_to_center_distances.shape[0] ):
            for col in range ( fa_borders_to_center_distances.shape[1] ):
                if fa_borders_to_center_distances[row][col] == 1:
                    fa_borders_to_center_distances[row][col] = sqrt ( ( row - self.__iit_tuned_center[0] ) ** 2 +
                                                                      ( col - self.__iit_tuned_center[1] ) ** 2 )
        self.__fa_borders_to_center_distances = fa_borders_to_center_distances

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
                neighbours = get_pixel_neighbours ( ( x, y ), ring_borders_map )
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
                        neighbours = get_pixel_neighbours ( ( x, y ), ring_borders_map )
                        for neighbour in neighbours:
                            if self.__array[neighbour[0]][neighbour[1]] == max_channel:
                                ring_borders_map[x][y] = 1.0
                                break
        self.__ring_borders_map = ring_borders_map

    def fine_tune_center ( self ):
        """
        When the ring borders have been detected, a line crossing the center should intercept the borders in a symmetric manner.
        Use this information to fine-tune the center position, and discover the borders' radii.
        """
        ia_noiseless_borders = self.__ring_borders_map - self.__noise_array

        ia_center_row_borders = ia_noiseless_borders[self.__iit_center[0],:]
        ia_left_partition  = ia_center_row_borders[:self.__iit_center[0] - 1]
        ia_right_partition = ia_center_row_borders[self.__iit_center[0] + 1:]
        i_first_left  = numpy.argmax ( ia_left_partition[::-1] )
        i_first_right = numpy.argmax ( ia_right_partition )
        i_tuned_col = self.__iit_center[1] + int ( ( i_first_left - i_first_right ) / 2 )

        ia_center_col_borders = ia_noiseless_borders[:,i_tuned_col]
        ia_bottom_partition  = ia_center_col_borders[:i_tuned_col - 1]
        ia_top_partition     = ia_center_col_borders[i_tuned_col + 1:]
        i_first_bottom  = numpy.argmax ( ia_bottom_partition[::-1] )
        i_first_top = numpy.argmax ( ia_top_partition )
        i_tuned_row = self.__iit_center[0] + int ( ( i_first_top - i_first_bottom ) / 2 )

        self.__iit_tuned_center = ( i_tuned_row, i_tuned_col )
        print ( "tuned center = %s" % str ( self.__iit_tuned_center ) )

        #ia_center_row = ia_noiseless_borders[self.__iit_tuned_center[0],:]
        #ia_right_partition = ia_center_row[self.__iit_tuned_center[0] + 1:]
        #il_radii = [ ]
        #while ( numpy.amax ( ia_right_partition ) == 1 ):
        #    i_radius = numpy.argmax ( ia_right_partition )
        #    il_radii.append ( i_radius )
        #    ia_right_partition[i_radius] = 0
        #
        #self.__il_borders_radii = il_radii

    #def get_borders_radii ( self ):
    #    if self.__il_borders_radii == [ ]:
    #        self.fine_tune_center ( )
    #
    #    return self.__il_borders_radii

    def get_borders_to_center_distances ( self ):
        return self.__fa_borders_to_center_distances

    def get_map ( self ):
        return self.__ring_borders_map

    def get_tuned_center ( self ):
        self.fine_tune_center ( )
        return self.__iit_tuned_center

def create_ring_borders_map ( log = print, array = None, iit_center = ( int, int ), noise_array = None ):
    start = time ( )
    log ( "create_ring_borders_map", end='' )

    ring_borders_object = ring_borders ( log = log, array = array, iit_center = iit_center, noise_array = noise_array )
    ring_borders_object.create_map_from_barycenter_array ( )
    
    log ( " %ds." % ( time ( ) - start ) )
    return ring_borders_object.get_map ( )

def create_borders_to_center_distances ( log = print, array = None, iit_center = ( int, int ), noise_array = None ):
    start = time ( )
    log ( "create_borders_to_center_distances", end='' )

    ring_borders_object = ring_borders ( log = log, array = array, iit_center = iit_center, noise_array = noise_array )
    ring_borders_object.create_map_from_barycenter_array ( )
    
    log ( " %ds." % ( time ( ) - start ) )
    return ring_borders_object.get_borders_to_center_distances ( )
