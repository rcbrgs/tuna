import logging
import math
import numpy
import threading
import time
import tuna

class noise_detector ( threading.Thread ):
    def __init__ ( self,
                   raw,
                   wrapped,
                   noise_mask_radius ):
        
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )

        self.raw = raw
        self.wrapped = wrapped
        self.noise_mask_radius = noise_mask_radius

        self.noise = None

        self.start ( )

    def run ( self ):
        """
        Will call detect_signalless, which will mask out pixels whose total signal (the curve below its profile) is less than X % of the average total signal per pixel.
        """
        noise_map = numpy.zeros ( shape = self.wrapped.array.shape, dtype = numpy.int16 )
        self.noise = tuna.io.can ( noise_map )
        self.detect_signalless ( )

    def detect_signalless ( self, threshold = 0.10 ):
        """
        Observing the profiles for pixels on the edges of a interferogram, one notices that there is much less signal in these regions, when the observable is centered on the field of view.
        This causes these regions to be highly susceptible to noise. To detect them, one finds the average value for the flux for a pixel, and masks out the pixels that are much lower than that. By default, much lower means less than 10% the flux.
        """
        start = time.time ( )

        # get an array of the sums of each profile:
        profile_sums = numpy.sum ( self.raw.array, 0 )

        average = numpy.average ( profile_sums )
        self.log.debug ( "average profile sum: %f" % average )

        signalless = numpy.where ( profile_sums < average * threshold,
                                   numpy.ones ( shape = self.noise.array.shape ),
                                   numpy.zeros ( shape = self.noise.array.shape ) )

        if self.noise_mask_radius != 1:
            for row in range ( signalless.shape [ 0 ] ):
                for col in range ( signalless.shape [ 1 ] ):
                    if signalless [ row ] [ col ] == 1:
                        include_noise_circle ( position = ( row, col ),
                                               radius = self.noise_mask_radius,
                                               array = signalless )
        
        self.noise.array = signalless

        self.log.debug ( "detect_signalless() took %ds." % ( time.time ( ) - start ) )

def include_noise_circle ( position = ( int, int ), radius = int, array = numpy.array ):
    for x in range ( position[0] - math.ceil ( radius ), position[0] + math.ceil ( radius ) + 1 ):
        for y in range ( position[1] - math.ceil ( radius ), position[1] + math.ceil ( radius ) + 1 ):
            if position_is_valid_pixel_address ( position = ( x, y ), array = array ):
                if math.sqrt ( ( x - position[0] )**2 + ( y - position[1] )**2 ) <= radius:
                    array[x][y] = 1

def position_is_valid_pixel_address ( position = ( int, int ), array = numpy.array ):
    if ( position[0] >= 0 and
         position[0] < array.shape[0] and
         position[1] >= 0 and
         position[1] < array.shape[1] ):
        return True
    return False
