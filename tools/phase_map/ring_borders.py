import logging
from math import sqrt
import numpy
import threading
import time
import tuna

class ring_border_detector ( threading.Thread ):
    def __init__ ( self, data, center, noise ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        super ( self.__class__, self ).__init__ ( )

        self.data = data
        self.center = center
        self.noise = noise

        self.borders = None
        self.discontinuities = None
        self.discontinuities_distances = None
        self.distances = None

        self.start ( )

    def run ( self ):
        start = time.time ( )

        self.detect_discontinuities ( )
        self.map_distances ( )
        self.create_synthetic_borders ( )
        self.distances = tuna.io.can ( self.borders )

        self.log.info ( "ring_border_detector took %ds." % ( time.time ( ) - start ) )

    def map_distances ( self ):
        """
        Supposing there is an array for the discontinuities, and the center has been found, produce an array with the distances from each discontinuity pixel to the center.
        """
        borders_to_center_distances = self.discontinuities - self.noise.array
        self.log.info ( "distances array 0% created." )
        last_percentage_logged = 0
        for row in range ( borders_to_center_distances.shape [ 0 ] ):
            percentage = 10 * int ( row / borders_to_center_distances.shape [ 0 ] * 10 )
            if percentage > last_percentage_logged:
                self.log.info ( "distances array %d%% created." % percentage )
                last_percentage_logged = percentage
            for col in range ( borders_to_center_distances.shape [ 1 ] ):
                if borders_to_center_distances [ row ] [ col ] == 1:
                    borders_to_center_distances [ row ] [ col ] = sqrt ( ( row - self.center [ 0 ] ) ** 2 +
                                                                         ( col - self.center [ 1 ] ) ** 2 )
        self.log.info ( "distances array 100%% created." )

        self.discontinuities_distances = borders_to_center_distances

    def detect_discontinuities ( self ):
        """
        From an unwrapped map and a noise map, create a map where pixels have 1 if they are noisy or have neighbours with a channel more distant than the channel distance threshold, 0 otherwise.
        """
        self.log.debug ( "Producing ring borders map." )
        ring_borders_map = numpy.zeros ( shape = self.data.array.shape )
        max_x = self.data.array.shape [ 0 ]
        max_y = self.data.array.shape [ 1 ]
        max_channel = numpy.amax ( self.data.array )
        threshold = max_channel / 2
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.noise.array [ x ] [ y ] == 1:
                    ring_borders_map [ x ] [ y ] = 1
                    continue
                neighbours = tuna.tools.get_pixel_neighbours ( ( x, y ), ring_borders_map )
                for neighbour in neighbours:
                    if self.noise.array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 0:
                        distance = self.data.array [ x ] [ y ] - \
                                   self.data.array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ]
                        if distance > threshold:
                            ring_borders_map [ x ] [ y ] = 1
                            break

        self.discontinuities = ring_borders_map

    def create_synthetic_borders ( self ):
        """
        From the distances map, find all distance ranges, simplify them to a single value per range, and produce a map with all pixels in that distance.
        """
        array = numpy.zeros ( shape = self.discontinuities_distances.shape )
        # collect all distinct radii values in a list
        distinct_radii = [ ]
        for row in range ( array.shape [ 0 ] ):
            for col in range ( array.shape [ 1 ] ):
                element = int ( self.discontinuities_distances [ row ] [ col ] )
                if element != 0:
                    if element not in distinct_radii:
                        distinct_radii.append ( element )
        sorted_radii = sorted ( distinct_radii )

        # Produce an array where pixels distant any sorted radii from the center have a value of 1.
        for row in range ( array.shape [ 0 ] ):
            for col in range ( array.shape [ 1 ] ):
                distance = sqrt ( ( self.center [ 0 ] - row ) ** 2 +
                                  ( self.center [ 1 ] - col ) ** 2 )
                #for radius in collapsed_radii:
                for radius in sorted_radii:
                    # These values were chosen so that the border will necessarily fall within a "band" with halfwidth of 2^1/2 pixels.
                    if ( ( distance > radius - 1.5 ) and
                         ( distance < radius + 1.5 ) ):
                        array [ row ] [ col ] = radius

        self.borders = array
