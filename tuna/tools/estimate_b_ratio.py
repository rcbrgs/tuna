# -*- coding: utf-8 -*-
"""This module's scope is the estimation of the b-ratio (the ratio between the
size of the pixels in the CCD and the focal length). 

Example::

    >>> import tuna
    >>> estimate = tuna.tools.estimate_b_ratio(radii = [100, 200], orders = [800, 801])
    >>> estimate
    0.00028933783055714126
"""
__version__ = '0.1.4'
__changelog = {
    "0.1.4": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.3": {"Tuna": "0.14.0", "Change": "updated documentation to new style."},
    "0.1.2": {"Change": "Added docstring."},
    "0.1.1": {"Change": "Error: was returning b**2 instead of its radix."},
    "0.1.0": {"Change": "First changelogged version."}
}

import logging
import math
import tuna

class BRatioEstimator(object):
    """Estimator object for finding the b-ratio. 

    The b-ratio is the ratio between the pixel size (of the interferometer pixel
    detector) and the focal length of the interferometers. In the absence of this
    information, it can be estimated by a geometrical relation between two
    "consecutive" rings in the same interferogram, which is what this estimator
    does.

    Parameters:

    * radii : list of floats
        Contains the concentric radii, sorted with smallest radius first.

    * orders : list of integers
        Contains the interference orders corresponding to the listed radii.
    """
    def __init__(self, radii, orders):
        self.log = logging.getLogger(__name__)
        
        self.orders = orders
        self.radii  = radii        

    def estimate(self):
        """The self.radii list should contain at least two radii.
        The innermost radii is of order "p", and the next one is of order "p-1".

        The estimate is calculated as:

        .. math::
          b^2 = \dfrac { 2 p_c - 1 } { p_c^2 ( r_{c-1}^2 - r_c^2 ) - 2 p_c r_{c-1}^2 + r_{c-1}^2 }

        (Thanks to Mr. Benoît Epinat for this model.)
        """
        if not isinstance(self.radii, list):
            self.log.error("radii should be a list!")
            return None

        if len(self.radii) < 2:
            self.log.error("Estimation requires at least 2 radii!")
            return None

        if not isinstance(self.orders, list):
            self.log.error("orders should be a list!")
            return None

        if len(self.orders) != len(self.radii):
            self.log.error("radii and orders should have the same length!")
            return None

        pc = self.orders[0]
        pc_1 = self.orders[1]

        r = self.radii[0]
        r_1 = self.radii[1]
        self.log.debug("r = {:e}, pc = {:e}; r_1 = {:e}, pc_1 = {:e}".format(
            r, pc, r_1, pc_1))

        b_squared = 2 * pc_1 / (pc**2 * (r_1**2 - r**2) \
                                - 2 * pc * r_1**2 + r_1**2)
        b = math.sqrt(b_squared)
        self.log.debug("b_ratio = {:e}".format(b))

        return b

def estimate_b_ratio(radii, orders):
    """From a list of radii, supposing each radius corresponds to the distance from a ring to the center, calculates b.

    Parameters:

    * radii : list of floats
        Contains the concentric radii, sorted with smallest radius first.

    * orders : list of integers
        Contains the interference orders corresponding to the listed radii.
    
    Returns:

    * estimate : float
        The value estimated for the b-ratio.
    """

    estimator = BRatioEstimator(radii, orders)
    estimate = estimator.estimate()
    return estimate
