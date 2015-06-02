import logging
from math import ceil, sqrt
import numpy
import threading
import time
import tuna

class noise_detector ( threading.Thread ):
    def __init__ ( self,
                   raw,
                   wrapped,
                   bad_neighbours_threshold,
                   channel_threshold,
                   noise_mask_radius ):
        
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )

        self.raw = raw
        self.wrapped = wrapped

        self.bad_neighbours_threshold = bad_neighbours_threshold
        self.channel_threshold = channel_threshold
        self.noise_mask_radius = noise_mask_radius

        self.noise = None

        self.start ( )

    def run ( self ):
        """
        This method will be applied to each pixel; it is at channel C.
        All neighbours should have their valye in the interval [C - epsilon, C + epsilon], or, if C = 0 or C = max, the neighbours could be wrapped to the previous/next order. 
        The final algorithm then considers the difference between the pixel and its neighbours' values, modulo the number of channels. If this results in a value above the channel_threshold, the neighbours is considered "bad".
        If a pixel has more than bad_neighbours_threshold "bad" neighbours, they are noisy and get value 1.
        Normal pixels get value 0.
        Returns the numpy array containing the binary noise map.

        Also, will call detect_signalless, which will mask out pixels whose total signal (the curve below its profile) is less than X % of the average total signal per pixel.
        
        Parameters:
        -----------
        - array is the numpy ndarray containing the wrapped.
        - bad_neighbours_threshold is the number of neighbours with bad 
        values that the algorithm will tolerate. It defaults to 7.
        - channel_threshold is the channel distance that will be tolerated. 
        It defaults to 1.
        """

        noise_map = numpy.zeros ( shape = self.wrapped.array.shape, dtype = numpy.int16 )
        self.noise = tuna.io.can ( noise_map )
        self.detect_signalless ( )
        return
        
        start = time.time ( )

        self.log.debug ( "bad_neighbours_threshold = %d" % self.bad_neighbours_threshold )

        noise_map = numpy.zeros ( shape = self.wrapped.array.shape, dtype = numpy.int16 )
        max_channel = numpy.amax ( self.wrapped.array )
        if ( max_channel == 0 ):
            self.noise = tuna.io.can ( noise_map )
            return

        noisy_pixels = 0
        self.log.info ( "noise array 0% created." )
        last_percentage_logged = 0
        for x in range ( self.wrapped.array.shape [ 0 ] ):
            percentage = 10 * int ( x / self.wrapped.array.shape [ 0 ] * 10 )
            if ( percentage > last_percentage_logged ):
                self.log.info ( "noise array %d%% created." % ( percentage ) )
                last_percentage_logged = percentage

            for y in range ( self.wrapped.array.shape [ 1 ] ):
                this_channel = self.wrapped.array [ x ] [ y ]
                if ( this_channel == 0 ):
                    continue

                neighbours = tuna.tools.get_pixel_neighbours ( ( x, y ), self.wrapped.array )
                # Since pixels in the borders of the canvas have less neighbours,
                # they start with those non-existing neighbours marked as bad.
                number_of_neighbours = len ( neighbours )
                bad_results = 8 - number_of_neighbours
                for neighbour in neighbours:
                    distance = abs ( self.wrapped.array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] - this_channel )
                    if distance > self.channel_threshold:
                        bad_results += 1
                    if ( bad_results > self.bad_neighbours_threshold ):
                        noisy_pixels += 1
                        include_noise_circle ( position = ( x, y ), radius = self.noise_mask_radius, array = noise_map )
                        continue
        self.log.info ( "noise array 100% created." )
        self.log.info ( "%d pixels were marked noisy." % noisy_pixels )

        self.noise = tuna.io.can ( noise_map )

        self.log.info ( "create_noise_array() took %ds" % ( time.time ( ) - start ) )

    def detect_signalless ( self, threshold = 0.10 ):
        """
        Observing the profiles for pixels on the edges of a interferogram, one notices that there is much less signal in these regions, when the observable is centered on the field of view.
        This causes these regions to be highly susceptible to noise. To detect them, one finds the average value for the flux for a pixel, and masks out the pixels that are much lower than that. By default, much lower means less than 10% the flux.
        """
        start = time.time ( )

        # get an array of the sums of each profile:
        profile_sums = numpy.sum ( self.raw.array, 0 )

        average = numpy.average ( profile_sums )
        self.log.info ( "average profile sum: %f" % average )

        signalless = numpy.where ( profile_sums < average * threshold,
                                   numpy.ones ( shape = self.noise.array.shape ),
                                   numpy.zeros ( shape = self.noise.array.shape ) )
        
        self.noise.array = signalless

        self.log.info ( "detect_signalless() took %ds." % ( time.time ( ) - start ) )

def include_noise_circle ( position = ( int, int ), radius = int, array = numpy.array ):
    for x in range ( position[0] - ceil ( radius ), position[0] + ceil ( radius ) + 1 ):
        for y in range ( position[1] - ceil ( radius ), position[1] + ceil ( radius ) + 1 ):
            if position_is_valid_pixel_address ( position = ( x, y ), array = array ):
                if sqrt ( ( x - position[0] )**2 + ( y - position[1] )**2 ) <= radius:
                    array[x][y] = 1

def position_is_valid_pixel_address ( position = ( int, int ), array = numpy.array ):
    if ( position[0] >= 0 and
         position[0] < array.shape[0] and
         position[1] >= 0 and
         position[1] < array.shape[1] ):
        return True
    return False
