from math import floor
import numpy
from time import time

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
        for row in range ( self.cube.max_row ):
            for col in range ( self.cube.max_col ):
                profile = self.__array[:,row,col]
                d_shoulder = self.get_fwhh ( profile = profile )

                shoulder_mask = numpy.zeros ( shape = ( self.cube.max_dep ) )
                multipliers = numpy.zeros ( shape = ( self.cube.max_dep ) )
                cursor = d_shoulder['i_left_shoulder']
                multiplier = 1
                multipliers[cursor] = multiplier
                shoulder_mask[cursor] = 1
                while ( cursor != d_shoulder['i_right_shoulder'] ):
                    cursor = self.get_right_channel ( channel = cursor, profile = profile )
                    multiplier += 1
                    multipliers[cursor] = multiplier
                    shoulder_mask[cursor] = 1
                
                weighted_photon_count = multipliers * profile
                weighted_sum = numpy.sum ( weighted_photon_count )
                shoulder_photon_count = shoulder_mask * profile
                shoulder_photon_count_sum = numpy.sum ( shoulder_photon_count )

                if shoulder_photon_count_sum == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = weighted_sum / shoulder_photon_count_sum

                shifted_center_of_mass = d_shoulder['i_left_shoulder'] - 1 + center_of_mass

                if shifted_center_of_mass != self.cube.max_dep:
                    ordered_shifted_center_of_mass = shifted_center_of_mass % ( self.cube.max_dep )
                
                barycenter_array[row][col] = ordered_shifted_center_of_mass

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

        i_left_shoulder = self.get_left_channel ( leftmost_hh )
        while ( ( profile [ i_left_shoulder ] - profile [ self.get_right_channel ( i_left_shoulder ) ] <= 0 ) and
                ( i_left_shoulder != max_height_index ) ):
            i_left_shoulder = self.get_left_channel ( i_left_shoulder )
        i_left_shoulder = self.get_right_channel ( i_left_shoulder )

        i_right_shoulder = self.get_right_channel ( rightmost_hh )
        while ( ( profile [ i_right_shoulder ] - profile [ self.get_left_channel ( i_right_shoulder ) ] <= 0 ) and
                ( i_right_shoulder != max_height_index ) ):
            i_right_shoulder = self.get_right_channel ( i_right_shoulder )
        i_right_shoulder = self.get_left_channel ( i_right_shoulder )
            
        il_shoulder_indices = [ i_left_shoulder ]
        cursor = i_left_shoulder
        while ( cursor != i_right_shoulder ):
            if cursor not in il_shoulder_indices:
                il_shoulder_indices.append ( cursor )
            cursor = self.get_right_channel ( cursor )

        fwhh_dict = { }
        fwhh_dict['max_height'] = max_height
        fwhh_dict['half_height'] = half_height
        fwhh_dict['max_height_index'] = max_height_index
        fwhh_dict['leftmost_hh'] = leftmost_hh
        fwhh_dict['rightmost_hh'] = rightmost_hh
        fwhh_dict['profile_indices'] = fwhh_profile_indices
        fwhh_dict['i_left_shoulder'] = i_left_shoulder
        fwhh_dict['i_right_shoulder'] = i_right_shoulder
        fwhh_dict['il_shoulder_indices'] = il_shoulder_indices
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

def create_barycenter_array ( array = None ):
    """
    Create a wrapped phase map using the barycenter of each spectrum as the pixel value.
    """
    i_start = time ( )
    print ( "create_barycenter_array", end='' )

    barycenter_object = barycenter ( array = array )
    fa_barycenter = barycenter_object.create_barycenter_using_peak ( )

    print ( " %ds." % ( time ( ) - i_start ) )
    return fa_barycenter
