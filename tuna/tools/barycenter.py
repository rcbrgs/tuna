"""
This module's scope is the creation of barycenter "maps" from Fabry-Pérot interferogram data.

The barycenter map is one of the so-called "wrapped" phase map types.

Example:

    >>> import tuna
    >>> import numpy
    >>> raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc_3_planes.fits" )
    >>> barycenter = tuna.plugins.run ( "Barycenter algorithm" ) ( data_can = raw )
    >>> barycenter.shape
    (512, 512)
"""

__version__ = "0.1.0"
changelog = {
    "0.1.0" : ( "0.15.0", "Updated example to use plugins." )
    }

from astropy.modeling import models, fitting
import logging
import math
import numpy
import threading
import time
import tuna
import warnings

class barycenter_detector ( threading.Thread ):
    """
    This class' responsibility is to generate barycenter maps from spectral cubes.

    Its algorithm utilizes a fitter to fit a parabola to each pixel, and find the barycenter from the fit parameters.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor expects the following parameters:

    * data : can
        Containing the interferograph data.    
    """
    def __init__ ( self, data ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.0"
        self.changelog = {
            "0.1.0" : "Tuna 0.14.0 : updated docstrings to new style."
            }
        
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )

        self.data = data
        self.__array = self.data.array
        self.__number_of_spectral_regions_array = None
        self.__photon_counts_array = None
        self.__number_spectral_peaks_array = None

        self.mask = numpy.mgrid [ 1 : self.__array.shape [ 0 ] + 1 ]
        
        self.barycenter = None
        self.result = None
        self.start ( )

    def run ( self ):
        """
        This method's goal is to wrap execution to be called from the thread's .start ( ) method.
        """
        start = time.time ( )

        result = self.create_barycenter ( )
        self.log.debug ( "result.shape = %s" % str ( result.shape ) )
        try:
            self.result = tuna.io.can ( array = result )
        except TypeError:
            self.result = tuna.io.can.can ( array = result )
        self.log.debug ( "self.result.array.shape = %s" % str ( self.result.array.shape ) )

        self.log.debug ( "Barycenter detection took %ds." % ( time.time ( ) - start ) )

    def create_barycenter ( self ):
        """
        This method's goal is to find the barycenter for each pixel by fitting a 1D gaussian model to each pixel's spectral data, and then calculating the barycenter of the gaussian.

        Returns:

        * barycenter : numpy.ndarray
            Containing the generated barycenter map.
        """
        barycenter = numpy.zeros ( shape = ( self.__array.shape [ 1 ],
                                             self.__array.shape [ 2 ] ) )
        planes_indexes = numpy.mgrid [ 0 : self.__array.shape [ 0 ] ]      
        # Supposing a single peak, a single Gaussian distribution should be ok.
        gaussian = models.Gaussian1D ( amplitude = 1.0, mean = self.__array.shape [ 0 ] / 2, stddev = 1 )
        fitter = fitting.LevMarLSQFitter ( )
        for row in range (  self.__array.shape [ 1 ] ):
            self.log.debug ( "barycenter at row %d" % row )
            for col in range ( self.__array.shape [ 2 ] ):
                profile = self.__array [ :, row, col ]
                # Single peak: centering the largest signal should center the profile.
                profile_max = numpy.argmax ( profile )
                roll = round ( self.__array.shape [ 0 ] / 2 ) - profile_max
                shifted_profile = numpy.roll ( profile, roll )
                with warnings.catch_warnings ( ):
                    warnings.simplefilter ( "ignore" )
                    fit = fitter ( gaussian, planes_indexes, shifted_profile )
                mean = fit.parameters [ 1 ]
                # From https://en.wikipedia.org/wiki/Gaussian_function:
                FWHH = 2.35482 * abs ( fit.parameters [ 2 ] )
                left_shoulder = max ( 0, math.floor ( mean - FWHH * 4 ) )
                right_shoulder = min ( self.__array.shape [ 0 ], math.ceil ( mean + FWHH * 4 ) )
                peak = shifted_profile [ left_shoulder : right_shoulder ]
                peak_center_of_mass = self.get_center_of_mass ( peak )
                rolled_center_of_mass = left_shoulder + peak_center_of_mass
                unrolled_center_of_mass = rolled_center_of_mass - roll
                moduled_center_of_mass = unrolled_center_of_mass % self.__array.shape [ 0 ]
                barycenter [ row ] [ col ] = moduled_center_of_mass
                if col == 0:
                    self.log.debug ( "(%d, %3d) prof = %s" % ( row, col, str ( profile ) ) )
                    self.log.debug ( "(%d, %3d) roll = %d" % ( row, col, roll ) )
                    self.log.debug ( "(%d, %3d) spro = %s" % ( row, col, str ( shifted_profile ) ) )
                    self.log.debug ( "(%d, %3d) ampl = %f, mean = %f, stddev = %f." % ( row, col, fit.parameters [ 0 ], mean, fit.parameters [ 2 ] ) )
                    self.log.debug ( "(%d, %3d) fwhh = %f." % ( row, col, FWHH ) )
                    self.log.debug ( "(%d, %3d) shou = [ %d : %d ]" % ( row, col, left_shoulder, right_shoulder ) )
                    self.log.debug ( "(%d, %3d) peak = %s" % ( row, col, str ( peak ) ) )
                    self.log.debug ( "(%d, %3d) pcen = %f" % ( row, col, peak_center_of_mass ) )
                    self.log.debug ( "(%d, %3d) rcen = %f" % ( row, col, rolled_center_of_mass ) )
                    self.log.debug ( "(%d, %3d) ucen = %f" % ( row, col, unrolled_center_of_mass ) )
                    self.log.debug ( "(%d, %3d) mcen = %f" % ( row, col, moduled_center_of_mass ) )
                    self.log.debug ( "(%d, %d) barycenter detected at %.3f using %.1f%% of the spectrum." %
                                    ( row, col, moduled_center_of_mass,
                                      peak.shape [ 0 ] / self.__array.shape [ 0 ] * 100 ) )

            self.log.debug ( "barycenter.shape = %s" % str ( barycenter.shape ) )
        return barycenter

    def get_center_of_mass ( self, peak ):
        """
        This method's goal is to calculate the center-of-mass of an array, assuming as the distance one "unit" of distance per column.

        Parameters:

        * peak: numpy.ndarray
            One dimensional data (spectra) corresponding to 1 pixel's "depth" in the cube.

        Returns:

        * center_of_mass : float
            The value of the "pseudo channel" where the center of mass resider, for this spectra.
        """
        total_mass = numpy.sum ( peak )
        if ( total_mass == 0 or
             peak == [ ] ):
            return 0
        #mask = numpy.mgrid [ 1 : peak.shape [ 0 ] + 1 ]
        weighted_mass = self.mask [ : peak.shape [ 0 ] ] * peak
        center_of_mass = numpy.sum ( weighted_mass ) / total_mass
        return center_of_mass
    
class barycenter_fast ( threading.Thread ):
    """
    This class' responsibility is to generate and store barycenter maps from spectral cubes. 

    Its algorithm uses geometric considerations to determine where is the center of mass for each spectrum, and is generally much faster than the algorithm using fitted data, with very similar numerical results. However, some pixelation is observed, when using this algorithm instead of the "slow" one.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor expects the following parameters:

    * data : can
        Containing the interferograph data.    
    """
    def __init__ ( self, data ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        super ( self.__class__, self ).__init__ ( )

        self.data = data
        self.__array = self.data.array
        self.__number_of_spectral_regions_array = None
        self.__photon_counts_array = None
        self.__number_spectral_peaks_array = None

        self.result = None
        self.start ( )

    def run ( self ):
        """
        This method's goal is to execute the main algorithm, when called by this object's threading.Thread.start ( ) method.
        """
        start = time.time ( )

        result = self.create_barycenter_using_peak ( )
        self.log.debug ( "result.shape = %s" % str ( result.shape ) )
        self.result = tuna.io.can.Can ( array = result )
        self.log.debug ( "self.result.array.shape = %s" % str ( self.result.array.shape ) )

        self.log.debug ( "Barycenter detection took %ds." % ( time.time ( ) - start ) )

    def create_barycenter_using_peak ( self ):
        """
        This method's goal is to generate the barycenter map using the peak method. 
        Will find the center of mass of each spectrum, using the shoulder-to-shoulder peak channels as the relevant signals. To understand what is meant by this, consider the profile of a pixel has the following appearance::
          
                      _   _
                    _/ \_/ \ 
           __      /        \    _
             \    /          \__/ \    /
              \__/                 \__/
          
           01234567890123456789012345678
                     1111111111222222222

        The FWHH channels would encompass the channels 8 to 17.
        But we want more signal, so we extend the channel interval until the first channel that would belong to another "peak", so the channels considered for the barycenter are actually the channels 4 to 20, inclusive.

        Once this "peak" is found, the center of mass for it is calculated, and the result is mapped onto the complete spectra, which yields the barycenter for that spectrum.

        Returns:

        * barycenter_array : numpy.ndarray
            Containing the barycenter map as calculated above, for each pixel in the input data.        
        """

        if self.__array.ndim != 3:
            return
            
        barycenter_array = numpy.ndarray ( shape = ( self.__array.shape [ 1 ], self.__array.shape [ 2 ] ) )

        # Linear algebra to produce the barycenter:
        # All calculations are made using arrays that are created with index 0 containing values in reference to the "leftmost" channel of the spectral range being considered.
        # In the end, this shifted result is shifted to the data position by adding the index for this "leftmos" channel.
        # The barycenter being the ratio of weighted-by-distance mass and mass, two auxiliary arrays are created. Both start as zero-valued arrays with the same size as the profile.
        # The "multipliers" gets the integer sequence 1, 2, 3, ... starting from the leftmost channel and ending in the rightmost channel of the spectral ROI.
        # The "shoulder_mask" gets the integer 1 at every index between the leftmost and rightmost channels in the spectral ROI.
        # The weighted-by-distance mass value is the profile times the multipliers array;
        # The total mass value is the profile times the shoulder_mask.
        
        self.log.debug ( "Barycenter 0% done." )
        last_percentage_logged = 0
        for row in range ( self.__array.shape [ 1 ] ):
            percentage = 10 * int ( row / self.__array.shape [ 1 ] * 10 )
            if percentage > last_percentage_logged:
                self.log.debug ( "Barycenter %d%% done." % ( percentage ) )
                last_percentage_logged = percentage
            for col in range ( self.__array.shape [ 2 ] ):
                profile = self.__array[:,row,col]
                shoulder = self.get_fwhh ( profile = profile )

                shoulder_mask = numpy.zeros ( shape = ( self.__array.shape [ 0 ] ) )
                multipliers = numpy.zeros ( shape = ( self.__array.shape [ 0 ] ) )
                cursor = shoulder['i_left_shoulder']
                multiplier = 1
                multipliers[cursor] = multiplier
                shoulder_mask[cursor] = 1
                cursor = self.get_right_channel ( channel = cursor, profile = profile )
                while ( cursor != self.get_right_channel ( channel = shoulder [ 'i_right_shoulder' ], 
                                                           profile = profile ) ):
                    multiplier += 1
                    multipliers[cursor] = multiplier
                    shoulder_mask[cursor] = 1
                    cursor = self.get_right_channel ( channel = cursor, profile = profile )
                
                weighted_photon_count = multipliers * profile
                weighted_sum = numpy.sum ( weighted_photon_count )
                shoulder_photon_count = shoulder_mask * profile
                shoulder_photon_count_sum = numpy.sum ( shoulder_photon_count )

                if shoulder_photon_count_sum == 0:
                    self.log.debug ( "At ( %d, %d ), shoulder_photon_count_sum == 0" % ( row, col ) )
                    self.print_fwhh ( shoulder )
                    center_of_mass = 0
                else:
                    center_of_mass = weighted_sum / shoulder_photon_count_sum

                shifted_center_of_mass = shoulder['i_left_shoulder'] - 1 + center_of_mass

                if shifted_center_of_mass != self.__array.shape [ 0 ]:
                    ordered_shifted_center_of_mass = shifted_center_of_mass % ( self.__array.shape [ 0 ] )
                
                barycenter_array[row][col] = ordered_shifted_center_of_mass
        self.log.info ( "Barycenter done." )

        return barycenter_array

    def get_fwhh ( self, profile = numpy.ndarray ):
        """
        This method's goal is to map "geometrical" features of the input spectra.        
        The features are the indices of the FWHH channels in the profile, and the relevant data for FWHH calculation.

        This is done using auxiliary methods to get the next channel to the right or left, wrapping around the end of the array as appropriate.
        First the FWHH values are found, by searching the first channel that has the maximal value in the profile, and adding channels left and right while their values are greater or equal to the half height of the maximal channel.

        Then this region is increased in both directions as long as the channels adjacent to the current spectral ROI have values smaller or equal to the "border" channels of the ROI. This extends the FWHH region to the "base" of the peak set that contains the FWHH.

        Parameters:

        * profile : numpy.ndarray
            Containing the spectrum to be mapped.

        Returns:

        * fwhh_dict : dictionary
            Containing the following entries::

                max_height          : The value contained in the channel with maximum signal.
                half_height         : Half of max_height.
                max_height_index    : The index of the channel with maximum signal.
                leftmost_hh         : The "leftmost" channel that has signal >= half_height.
                rightmost_hh        : The "rightmost" channel that has signal >= half_height.
                profile_indices     : All indices of the spectra that are contained in the "half height peak".
                i_left_shoulder     : The index of the leftmost channel of the peak.
                i_right_shoulder    : The index of the rightmost channel of the peak.
                il_shoulder_indices : All indices of the spectra that are contained in the peak.
        """

        max_height = numpy.amax ( profile )
        max_height_index = numpy.argmax ( profile )
        half_height = max_height / 2
        
        leftmost_hh = self.get_left_channel ( max_height_index )
        while ( profile[leftmost_hh] >= half_height and
                leftmost_hh != max_height_index ):
            leftmost_hh = self.get_left_channel ( channel = leftmost_hh, profile = profile )
        leftmost_hh = self.get_right_channel ( channel = leftmost_hh, profile = profile )

        rightmost_hh = self.get_right_channel ( max_height_index )
        while ( profile[rightmost_hh] >= half_height and
                rightmost_hh != max_height_index ):
            rightmost_hh = self.get_right_channel ( channel = rightmost_hh, profile = profile )
        rightmost_hh = self.get_left_channel ( channel = rightmost_hh, profile = profile )

        fwhh_profile_indices = [ leftmost_hh, max_height_index, rightmost_hh ]
        cursor = leftmost_hh
        while ( cursor != rightmost_hh ):
            if cursor not in fwhh_profile_indices:
                fwhh_profile_indices.append ( cursor )
            cursor = self.get_right_channel ( cursor )

        # Using only the FWHH channels causes pixelation of the phase map,
        # therefore the whole peak is used, starting with the FWHH.

        left_shoulder = leftmost_hh
        while ( ( profile [ self.get_left_channel ( left_shoulder ) ] - \
                  profile [ left_shoulder ] <= 0 ) and
                ( self.get_left_channel ( left_shoulder ) != rightmost_hh ) ):
            left_shoulder = self.get_left_channel ( left_shoulder )

        right_shoulder = rightmost_hh
        while ( ( profile [ self.get_right_channel ( right_shoulder ) ] - \
                  profile [ right_shoulder ] <= 0 ) and
                ( self.get_right_channel ( right_shoulder ) != left_shoulder ) ):
            right_shoulder = self.get_right_channel ( right_shoulder )
            
        shoulder_indices = [ left_shoulder ]
        cursor = left_shoulder
        while ( cursor != right_shoulder ):
            if cursor not in shoulder_indices:
                shoulder_indices.append ( cursor )
            cursor = self.get_right_channel ( cursor )

        fwhh_dict = { }
        fwhh_dict['max_height'] = max_height
        fwhh_dict['half_height'] = half_height
        fwhh_dict['max_height_index'] = max_height_index
        fwhh_dict['leftmost_hh'] = leftmost_hh
        fwhh_dict['rightmost_hh'] = rightmost_hh
        fwhh_dict['profile_indices'] = fwhh_profile_indices
        fwhh_dict['i_left_shoulder'] = left_shoulder
        fwhh_dict['i_right_shoulder'] = right_shoulder
        fwhh_dict['il_shoulder_indices'] = shoulder_indices
        return fwhh_dict
        
    def get_left_channel ( self, channel = int,  profile = numpy.ndarray ):
        """
        This method's goal is to find the next channel 'to the left' in the profile. 
        If the channel is the leftmost channel in the profile, consider the last channel as its left neighbour.

        Parameters:

        * channel : int
            The channel for which we want to find the left "neighbour".

        * profile : numpy.ndarray
            The unidimensional profile.

        Returns:

        * unnamed variable : integer
            The index of the channel to the "left" of the input channel.
        """
        if channel == 0:
            return self.__array.shape [ 0 ] - 1
        else:
            return channel - 1

    def get_right_channel ( self, channel = int,  profile = numpy.ndarray ):
        """
        This method's goal is to find the next channel 'to the right' in the profile. 
        If the channel is the last channel in the profile, consider the first channel as its right neighbour.

        Parameters:

        * channel : int
            The channel for which we want to find the right "neighbour".

        * profile : numpy.ndarray
            The unidimensional profile.

        Returns:

        * unnamed variable : integer
            The index of the channel to the "right" of the input channel.
        """
        if ( channel == self.__array.shape [ 0 ] - 1 ):
            return 0
        else:
            return channel + 1

    def print_fwhh ( self, fwhh_dict ):
        """
        This method's goal is to output to the current logger, with debug priority, the values contained in the fwhh_dict parameter.

        Parameters:

        * fwhh_dict : dictionary
             Structure with the same fields as specified in the self.get_fwhh ( ) method.
        """
        self.log.debug ( "max_height = %d" % fwhh_dict['max_height'] )
        self.log.debug ( "half_height = %d" % fwhh_dict['half_height'] )
        self.log.debug ( "max_height_index = %d" % fwhh_dict['max_height_index'] )
        self.log.debug ( "leftmost_hh = %d" % fwhh_dict['leftmost_hh'] )
        self.log.debug ( "rightmost_hh = %d" % fwhh_dict['rightmost_hh'] )
        self.log.debug ( "profile_indices = %s" % str ( fwhh_dict['profile_indices'] ) )
        self.log.debug ( "i_left_shoulder = %d" % fwhh_dict['i_left_shoulder'] )
        self.log.debug ( "i_right_shoulder = %d" % fwhh_dict['i_right_shoulder'] )
        self.log.debug ( "il_shoulder_indices = %s" % str ( fwhh_dict['il_shoulder_indices'] ) )

def barycenter_geometry ( data_can : tuna.io.can ) -> tuna.io.can:
    """
    This function's goal is to conveniently return an array of the barycenter position for each pixel of the input.

    Arguments:

    * data_can : tuna.io.can
        Should contain a 3D cube of raw Fabry-Pérot data.

    Returns:

    * tuna.io.can
        Containing a 2D array of floats, where each point is the barycenter of the respective spectrum on the input data.
    """

    detector = barycenter_fast ( data = data_can )
    detector.join ( )
    return detector.result

def barycenter_polynomial_fit ( data_can : tuna.io.can ) -> tuna.io.can:
    """
    This function's goal is to conveniently return an array of the barycenter position for each pixel of the input.

    Arguments:

    * data_can : tuna.io.can
        Should contain a 3D cube of raw Fabry-Pérot data.

    Returns:

    * tuna.io.can
        Containing a 2D array of floats, where each point is the barycenter of the respective spectrum on the input data.
    """

    detector = barycenter_detector ( data = data_can )
    detector.join ( )
    return detector.result
