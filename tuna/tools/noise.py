# -*- coding: utf-8 -*-
"""This module's scope is the detection of noise in Fabry-Pérot interferographs.

Example::

    >>> import tuna
    >>> raw = tuna.io.read("tuna/test/unit/unit_io/adhoc.ad3")
    >>> barycenter = tuna.plugins.run("Barycenter algorithm")(data_can = raw)
    >>> noise = tuna.plugins.run("Noise detector")(raw = raw, \
                                                   wrapped = barycenter.result, \
                                                   noise_mask_radius = 1, \
                                                   noise_threshold = 1)
    >>> noise.array[500 : 511, 500]
    array([ 1.,  0.,  1.,  1.,  0.,  1.,  1.,  1.,  1.,  1.,  1.])
"""
__version__ = "0.1.1"
__changelog = {
    "0.1.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.0": {"Tuna": "0.15.0", "Change": "Renamed 'raw' argument of " \
              "detect_noise to 'data'."}
}

import logging
import math
import numpy
import threading
import time
import tuna

class NoiseDetector(threading.Thread):
    """This class is responsible for detecting noise from a raw Fabry-Pérot
    interferograph.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts
    its thread execution. Clients are expected to use its .join ( ) method before
    using its results.

    The algorithm consists of creating a temporary array, summing the data on
    "depth" or spectra, for each pixel. If a threshold is passed on the input, it
    is the minimal value for a pixel be considered "non noisy". If no threshold
    was supplied by the user, the algorithm will search for the smallest
    percentile on the temporary array which is non-null. The value that
    corresponds to this percentile will be used as the threshold.

    The noise_mask_radius is useful to "fill" small gaps inside noise regions.
    Some tools (such as the ones used to produce fsr maps) relie on the noise
    being made of "continuous" pixel sets. By increasing this parameter, it is
    possible to force noisy regions to overlap and become "continuous", if they
    aren't.

    Its constructor expects the following parameters:

    * raw : numpy.ndarray 
        Containing the raw interferometry data.

    * wrapped : numpy.ndarray
        Containing the wrapped phase map.

    * noise_mask_radius : integer : 1
        Encoding the radius (in pixels) of the circle to be marked as noisy around each pixel detected as noisy.

    * noise_threshold : float : None
        Encoding the minimum value to be considered signal.
    """
    def __init__(self,
                 raw : tuna.io.Can,
                 wrapped : tuna.io.Can,
                 noise_mask_radius : int = 1,
                 noise_threshold : float = None ) -> None:
        super(self.__class__, self).__init__()
        self.log = logging.getLogger(__name__)

        self.raw = raw
        self.wrapped = wrapped
        self.noise_mask_radius = noise_mask_radius
        self.noise_threshold = noise_threshold
        
        self.noise = None

        self.start()

    def run(self):
        """Method required by :ref:`threading_label`, which allows parallel
        execution in a separate thread.

        The execution creates a zero-filled numpy.ndarray, fills it with the
        noise values as detected by the method self.detect_signalless() and
        then updates Tuna's database through the method self.refresh_database().
        """
        noise_map = numpy.zeros(shape = self.wrapped.array.shape,
                                dtype = numpy.int16)
        self.noise = tuna.io.Can(noise_map)
        self.detect_signalless(self.noise_threshold)
        self.refresh_database()

    def detect_signalless(self, threshold):
        """Mask out pixels whose total signal (the curve below its profile) is
        less than X % of the average total signal per pixel.
        Observing the profiles for pixels on the edges of a interferogram, one
        notices that there is much less signal in these regions, when the
        observable is centered on the field of view.
        This causes these regions to be highly susceptible to noise. To detect
        them, one finds the average value for the flux for a pixel, and masks out
        the pixels that are much lower than that. By default, much lower means
        less than 10% the flux.

        Parameters:

        * threshold : float
            Sets the minimal value for a pixel data be considered signal.
        """
        start = time.time ( )

        # get an array of the sums of each profile:
        profile_sums = numpy.sum(self.raw.array, 0)

        if self.noise_threshold != None:
            lower_value = self.noise_threshold
        else:
            lower_percentile = tuna.tools.find_lowest_nonnull_percentile(
                profile_sums)
            lower_value = numpy.percentile(profile_sums, lower_percentile)
            self.log.debug("lower_percentile = {}, lower_value = {:.2e}".format(
                lower_percentile, lower_value))

        signalless = numpy.where(profile_sums <= lower_value,
                                 numpy.ones(shape = self.noise.array.shape),
                                 numpy.zeros(shape = self.noise.array.shape))

        noise = numpy.zeros(shape = self.noise.array.shape)
        for row in range(signalless.shape[0]):
            for col in range(signalless.shape[1]):
                if signalless[row][col] == 1:
                    include_noise_circle(position = (row, col),
                                         radius = self.noise_mask_radius,
                                         array = noise)
        
        self.noise.array = noise

        self.log.info("Noise map created with lower_value = {}.".format(
            lower_value))
        self.log.debug("detect_signalless() took %ds." % (time.time() - start))

    def refresh_database ( self ):
        """Attempts to update the database with information about the result of a
        noise object.

        First, it obtains the hash of the current noise array. Then, it attempts
        to find the database record related to that hash. If found, the record is
        updated; otherwise, it is created.
        """
        digest = tuna.tools.get_hash_from_array(self.noise.array)
        record = tuna.db.select_record('noise', {'hash': digest})
        function = tuna.db.insert_record
        if record:
            function = tuna.db.update_record
        threshold = 0
        if self.noise_threshold:
            threshold = self.noise_threshold
        function('noise', {'hash': digest,
                           'radius': self.noise_mask_radius,
                           'threshold': threshold})

def include_noise_circle(position = (int, int),
                         radius = int, array = numpy.array):
    """"Draw" a circle with center position, radius radius in the array array,
    using the value 1 as its filling.

    Parameters:

    * position : tuple of 2 integers
        Corresponding to the center of the circle to be masked.

    * radius : integer
        Containing the length (in pixels) of the circle to be masked.

    * array : numpy.ndarray
        Specifies where the mask is to be drawn.
    """
    for col in range(position[0] - radius, position[0] + radius):
        for row in range(position[1] - radius, position[1] + radius):
            if position_is_valid_pixel_address(position = (col, row),
                                               array = array):
                if math.sqrt((col - position[0])**2 \
                             + (row - position[1])**2) <= radius:
                    array[col][row] = 1

def position_is_valid_pixel_address(position = (int, int), array = numpy.array):
    """Return True if the argument position is a valid coordinate of the input
    array.

    Parameters:

    * position : tuple of 2 integers
        Encoding a possible coordinate of the input array.

    * array : numpy.ndarray
        The array where the position validness is to be probed.
    """
    if (position[0] >= 0 and
        position[0] < array.shape[0] and
        position[1] >= 0 and
        position[1] < array.shape[1]):
        return True
    return False

def detect_noise(data: tuna.io.Can,
                 wrapped: tuna.io.Can,
                 noise_mask_radius: int = 1,
                 noise_threshold: float = None) -> tuna.io.Can:
    """Conveniently return a numpy.ndarray containing the noise map calculated
    from the input parameters.
    """
    detector = NoiseDetector(raw = data,
                             wrapped = wrapped,
                             noise_mask_radius = noise_mask_radius,
                             noise_threshold = noise_threshold )
    detector.join()
    return detector.noise
