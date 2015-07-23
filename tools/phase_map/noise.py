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
                   noise_mask_radius,
                   noise_threshold ):
        
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = '0.1.3'
        self.changelog = {
            '0.1.3'  : "Simplified noise radius loop to fix it.",
            '0.1.2'  : "Made threshold default to lowest nonnull percentile value, overridable.",
            '0.1.1'  : "Completed support for noise_threhsold parameter.",
            '0.1.0'  : "First changelogged version."
            }

        self.raw = raw
        self.wrapped = wrapped
        self.noise_mask_radius = noise_mask_radius
        self.noise_threshold = noise_threshold
        
        self.noise = None

        self.start ( )

    def run ( self ):
        """
        Will call detect_signalless, which will mask out pixels whose total signal (the curve below its profile) is less than X % of the average total signal per pixel.
        """
        noise_map = numpy.zeros ( shape = self.wrapped.array.shape, dtype = numpy.int16 )
        self.noise = tuna.io.can ( noise_map )
        self.detect_signalless ( self.noise_threshold )

    def detect_signalless ( self, threshold ):
        """
        Observing the profiles for pixels on the edges of a interferogram, one notices that there is much less signal in these regions, when the observable is centered on the field of view.
        This causes these regions to be highly susceptible to noise. To detect them, one finds the average value for the flux for a pixel, and masks out the pixels that are much lower than that. By default, much lower means less than 10% the flux.
        """
        start = time.time ( )

        # get an array of the sums of each profile:
        profile_sums = numpy.sum ( self.raw.array, 0 )

        if self.noise_threshold != None:
            lower_value = self.noise_threshold
        else:
            lower_percentile = tuna.tools.find_lowest_nonnull_percentile ( profile_sums )
            lower_value = numpy.percentile ( profile_sums, lower_percentile )
            self.log.debug ( "lower_percentile = {}, lower_value = {:.2e}".format ( lower_percentile,
                                                                                    lower_value ) )

        signalless = numpy.where ( profile_sums <= lower_value,
                                   numpy.ones ( shape = self.noise.array.shape ),
                                   numpy.zeros ( shape = self.noise.array.shape ) )

        noise = numpy.zeros ( shape = self.noise.array.shape )
        for row in range ( signalless.shape [ 0 ] ):
            for col in range ( signalless.shape [ 1 ] ):
                if signalless [ row ] [ col ] == 1:
                    include_noise_circle ( position = ( row, col ),
                                           radius = self.noise_mask_radius,
                                           array = noise )
        
        self.noise.array = noise

        self.log.info ( "Noise map created with lower_value = {}.".format ( lower_value ) )
        self.log.debug ( "detect_signalless() took %ds." % ( time.time ( ) - start ) )

def include_noise_circle ( position = ( int, int ), radius = int, array = numpy.array ):
    for     col in range ( position [ 0 ] - radius, position [ 0 ] + radius ):
        for row in range ( position [ 1 ] - radius, position [ 1 ] + radius ):
            if position_is_valid_pixel_address ( position = ( col, row ), array = array ):
                if math.sqrt ( ( col - position [ 0 ] )**2 + ( row - position [ 1 ] )**2 ) <= radius:
                    array [ col ] [ row ] = 1

def position_is_valid_pixel_address ( position = ( int, int ), array = numpy.array ):
    if ( position[0] >= 0 and
         position[0] < array.shape[0] and
         position[1] >= 0 and
         position[1] < array.shape[1] ):
        return True
    return False
