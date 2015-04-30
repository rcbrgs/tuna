from math import floor
import numpy
from time import time
import tuna

class spectrum_cube ( object ):
    """
    Helper class to the barycenter class; contains metadata about the profile.
    """
    def __init__ ( self, log = print ):
        super ( spectrum_cube, self ).__init__ ( )
        self.log = log
        
        self.dep_index = 0
        self.row_index = 1
        self.col_index = 2
        self.max_dep = 0
        self.max_row = 0
        self.max_col = 0
        self.channel_range = 0
        self.channel_range_center = 0

class barycenter ( object ):
    """
    Class to generate and store barycenter maps from spectral cubes.
    """
    def __init__ ( self, array = None, log = print ):
        super ( barycenter, self ).__init__ ( )
        self.log = log

        self.__array = array
        self.__number_of_spectral_regions_array = None
        self.__photon_counts_array = None
        self.__number_spectral_peaks_array = None
        self.cube = spectrum_cube ( log = self.log )
        self.profile = None
    
    def create_barycenter_using_peak ( self ):
        """
        Returns a barycenter array from the input array, using the shoulder-to-shoulder peak channels as the relevant signals.
        Consider the profile of a pixel has the following appearance:
                   _   _
                 _/ \_/ \
        __      /        \    _
          \    /          \__/ \    /
           \__/                 \__/

        01234567890123456789012345678
                  1111111111222222222

        The FWHH channels would encompass the channels 8 to 17.
        But we want more signal, so we extend the channel interval until the first channel that would belong to another "peak", so the channels considered for the barycenter are actually the channels 4 to 20, inclusive.

        """
        #self.log ( "Creating barycenter array from peak channels." )
        if self.__array.ndim != 3:
            return
            
        self.cube.max_dep = self.__array.shape[self.cube.dep_index]
        self.cube.max_row = self.__array.shape[self.cube.row_index]
        self.cube.max_col = self.__array.shape[self.cube.col_index]
        barycenter_array = numpy.ndarray ( shape = ( self.cube.max_row, self.cube.max_col ) )

        # Linear algebra to produce the barycenter:
        # All calculations are made using arrays that are created with index 0 containing values in reference to the "leftmost" channel of the spectral range being considered.
        # In the end, this shifted result is shifted to the data position by adding the index for this "leftmos" channel.
        # The barycenter being the ratio of weighted-by-distance mass and mass, two auxiliary arrays are created. Both start as zero-valued arrays with the same size as the profile.
        # The "multipliers" gets the integer sequence 1, 2, 3, ... starting from the leftmost channel and ending in the rightmost channel of the spectral ROI.
        # The "shoulder_mask" gets the integer 1 at every index between the leftmost and rightmost channels in the spectral ROI.
        # The weighted-by-distance mass value is the profile times the multipliers array;
        # The total mass value is the profile times the shoulder_mask.
        
        self.log ( "info: creating barycenter 0% done." )
        last_percentage_logged = 0
        for row in range ( self.cube.max_row ):
            percentage = 10 * int ( row / self.cube.max_row * 10 )
            if percentage > last_percentage_logged:
                self.log ( "info: creating barycenter %d%% done." % ( percentage ) )
                last_percentage_logged = percentage
            for col in range ( self.cube.max_col ):
                profile = self.__array[:,row,col]
                shoulder = self.get_fwhh ( profile = profile )

                shoulder_mask = numpy.zeros ( shape = ( self.cube.max_dep ) )
                multipliers = numpy.zeros ( shape = ( self.cube.max_dep ) )
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
                    self.log ( "debug: at ( %d, %d ), shoulder_photon_count_sum == 0" % ( row, col ) )
                    self.print_fwhh ( shoulder )
                    center_of_mass = 0
                else:
                    center_of_mass = weighted_sum / shoulder_photon_count_sum

                shifted_center_of_mass = shoulder['i_left_shoulder'] - 1 + center_of_mass

                if shifted_center_of_mass != self.cube.max_dep:
                    ordered_shifted_center_of_mass = shifted_center_of_mass % ( self.cube.max_dep )
                
                barycenter_array[row][col] = ordered_shifted_center_of_mass
        self.log ( "info: creating barycenter 100% done." )

        return barycenter_array

    def get_fwhh ( self, profile = numpy.ndarray ):
        """
        Returns a dict containing the indices of the FWHH channels in the profile, and the relevant data for FWHH calculation.

        This is done using auxiliary methods to get the next channel to the right or left, wrapping around the end of the array as appropriate.
        First the FWHH values are found, by searching the first channel that has the maximal value in the profile, and adding channels left and right while their values are greater or equal to the half height of the maximal channel.

        Then this region is increased in both directions as long as the channels adjacent to the current spectral ROI have values smaller or equal to the "border" channels of the ROI. This extends the FWHH region to the "base" of the peak set that contains the FWHH.
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
        Returns the next channel 'to the left' in the profile.
        """
        if channel == 0:
            return self.cube.max_dep - 1
        else:
            return channel - 1

    def get_right_channel ( self, channel = int,  profile = numpy.ndarray ):
        """
        Returns the next channel 'to the right' in the profile.
        """
        if ( channel == self.cube.max_dep - 1 ):
            return 0
        else:
            return channel + 1

    def print_fwhh ( self, fwhh_dict ):
        self.log ( "debug: max_height = %d" % fwhh_dict['max_height'] )
        self.log ( "debug: half_height = %d" % fwhh_dict['half_height'] )
        self.log ( "debug: max_height_index = %d" % fwhh_dict['max_height_index'] )
        self.log ( "debug: leftmost_hh = %d" % fwhh_dict['leftmost_hh'] )
        self.log ( "debug: rightmost_hh = %d" % fwhh_dict['rightmost_hh'] )
        self.log ( "debug: profile_indices = %s" % str ( fwhh_dict['profile_indices'] ) )
        self.log ( "debug: i_left_shoulder = %d" % fwhh_dict['i_left_shoulder'] )
        self.log ( "debug: i_right_shoulder = %d" % fwhh_dict['i_right_shoulder'] )
        self.log ( "debug: il_shoulder_indices = %s" % str ( fwhh_dict['il_shoulder_indices'] ) )

def detect_barycenters ( array = None,
                         log = print ):
    """
    Create a wrapped phase map using the barycenter of each spectrum as the pixel value.
    """
    start = time ( )

    barycenter_object = barycenter ( array = array, log = log )
    result = barycenter_object.create_barycenter_using_peak ( )
    result_can = tuna.io.can ( log = log,
                               array = result )

    log ( "info: create_barycenter_array() took %ds." % ( time ( ) - start ) )
    return result_can
