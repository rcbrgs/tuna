# -*- coding: utf-8 -*-
"""This module's scope is wavelength calibration for high resolution, unwrapped
phase maps.

Example::

    >>> import tuna
    >>> unwrapped = tuna.io.read("tuna/test/unit/unit_io/G092_unwrapped.fits")
    >>> wavelength_calibrator = tuna.tools.wavelength.wavelength_calibrator(
            unwrapped, calibration_wavelength = 6598.953125, 
            free_spectral_range = 8.36522123894, interference_order = 791,
            interference_reference_wavelength = 6562.7797852,
            number_of_channels = 36, rings_center = (219, 255),
            scanning_wavelength = 6616.89)
    >>> wavelength_calibrator.join()
    >>> wavelength_calibrator.calibrated.array[150 : 200]
    array([[ 74.04817666,  73.55519697,  72.94114164, ...,  73.3628646 ,
             73.92926326,  74.35776   ],
           [ 73.86583775,  73.40994124,  72.98461314, ...,  73.31395047,
             73.79109333,  74.38074642],
           [ 73.79373484,  73.25194294,  72.80179596, ...,  73.26917593,
             73.65012203,  74.14601242],
           ..., 
           [ 70.3757617 ,  69.84531033,  69.27819624, ...,  69.75067727,
             70.17056757,  70.76731326],
           [ 70.404398  ,  69.77546764,  69.36459732, ...,  69.78971195,
             70.14732239,  70.67475633],
           [ 70.33776   ,  69.79072167,  69.25640406, ...,  69.63204571,
             69.93539779,  70.58647794]])
"""

import logging
import math
import numpy
import threading
import time
import tuna

class WavelengthCalibrator(threading.Thread):
    """This class is responsible for producing the wavelength calibrated cube
    from the phase map cube.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts
    its thread execution. Clients are expected to use its .join ( ) method before
    using its results.

    Its constructor expects the following parameters:

    * unwrapped_phase_map : numpy.ndarray
        Contains the data to be calibrated.

    * calibration_wavelength : float
        The value in Angstroms for the wavelength used to calibrate the data.

    * free_spectral_range : float 
        The value in Angstroms for the bandwidth of one interference order.

    * interference_order : integer
        The number of interference orders expected for this wavelength.

    * interference_reference_wavelength : float 
        The number of interference orders expected for the reference wavelength.

    * number_of_channels : integer
        Corresponds to the number of planes in the original data cube.

    * rings_center : dictionary
        A structure equivalent to the one produced by
        :ref:`tuna_tools_spectral_rings_fitter_label`.

    * scanning_wavelength : float
        The value in Angstroms of the wavelength scanned.
    """
    def __init__(self,
                 unwrapped_phase_map,
                 calibration_wavelength,
                 free_spectral_range,
                 interference_order,
                 interference_reference_wavelength,
                 number_of_channels,
                 rings_center,
                 scanning_wavelength):
        super(self.__class__, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        self.unwrapped_phase_map = unwrapped_phase_map
        
        self.calibration_wavelength = calibration_wavelength
        self.free_spectral_range = free_spectral_range
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.number_of_channels = number_of_channels
        self.rings_center = rings_center
        self.scanning_wavelength = scanning_wavelength

        self.channel_width = number_of_channels

        self.calibrated = None

        self.start()

    def calibrate(self):
        """Discover the value of the wavelength at the apex of the parabola that
        fits the data.
        """
        self.log.debug("self.interference_order = %f" % self.interference_order)
        self.log.debug("self.interference_reference_wavelength = %f" %
                       self.interference_reference_wavelength)
        self.log.debug("self.calibration_wavelength = %f" %
                       self.calibration_wavelength)
        order_calibration = round(self.interference_order \
                                  * self.interference_reference_wavelength \
                                  / self.calibration_wavelength)
        self.log.debug("order_calibration = %f" % order_calibration)
        order_scanning = round(self.interference_order \
                               * self.interference_reference_wavelength \
                               / self.scanning_wavelength)
        self.log.debug("order_scanning = %f" % order_scanning)
        calculated_FSR = self.scanning_wavelength / order_scanning
        self.log.debug("input FSR = %f, calculated FSR = %f" % (
            self.free_spectral_range, calculated_FSR))

        decalage = self.channel_width \
                   * (0.5 - (self.scanning_wavelength \
                             - self.calibration_wavelength \
                             * (order_calibration / order_scanning)) \
                      / self.free_spectral_range)
        self.log.debug("decalage = %f" % decalage)
        calibrated = numpy.copy(self.unwrapped_phase_map.array)
        calibrated -= decalage

        if (self.rings_center[0] < 0 or
            self.rings_center[1] < 0 or
            self.rings_center[0] > self.unwrapped_phase_map.array.shape[0] or
            self.rings_center[1] > self.unwrapped_phase_map.array.shape[1]):
            self.log.error("Cannot wavelength-calibrate when the center is not "\
                           "a valid pixel! Copying the unwrapped phase map as " \
                           "the result.")
            self.calibrated = tuna.io.Can(array = self.unwrapped_phase_map.array)
            return

        self.log.debug("self.number_of_channels = %d" % self.number_of_channels)
        if calibrated[self.rings_center[0]][self.rings_center[1]] < 0:
            ceiling_offset = math.ceil(-numpy.amin(calibrated) \
                                       / self.number_of_channels) \
                                       * self.number_of_channels
            self.log.debug("ceiling_offset = %f" % ceiling_offset)
            calibrated += ceiling_offset

        if calibrated[self.rings_center[0]][self.rings_center[1]] \
           > self.number_of_channels:
            floor_offset = math.floor(numpy.amin(calibrated) \
                                      / self.number_of_channels) \
                                      * self.number_of_channels
            calibrated -= floor_offset
            self.log.debug("floor_offset = %f" % floor_offset)

        self.log.debug("self.unwrapped_phase_map.get_array().ndim == %d" %
                       self.unwrapped_phase_map.ndim)
        self.log.debug("calibrated.ndim == %d" % calibrated.ndim)

        self.calibrated = tuna.io.Can(array = calibrated)

    def run(self):
        """Method required by :ref:`threading_label`, which allows parallel
        exection in a separate thread.
        """
        start = time.time()

        self.calibrate()

        self.log.info("Wavelength calibration done.")
        self.log.debug("wavelength_calibration() took %ds." % (
            time.time() - start))
