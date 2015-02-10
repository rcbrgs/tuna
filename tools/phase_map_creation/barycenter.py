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
    
    def run ( self ):
        """
        Returns a barycenter array from the input array, using the FWHH channels as the relevant signals.
        """
        #self.log ( "Creating barycenter array from FWHH channels." )
        if self.__array.ndim != 3:
            return
            
        self.cube.max_dep = self.__array.shape[self.cube.dep_index]
        self.cube.max_row = self.__array.shape[self.cube.row_index]
        self.cube.max_col = self.__array.shape[self.cube.col_index]
        barycenter_array = numpy.ndarray ( shape = ( self.cube.max_row, self.cube.max_col ) )

        for row in range ( self.cube.max_row ):
            for col in range ( self.cube.max_col ):
                profile = self.__array[:,row,col]
                fwhh = self.get_fwhh ( profile = profile )

                fwhh_mask = numpy.zeros ( shape = ( self.cube.max_dep ) )
                multipliers = numpy.zeros ( shape = ( self.cube.max_dep ) )
                cursor = fwhh['leftmost_hh']
                multiplier = 1
                multipliers[cursor] = multiplier
                fwhh_mask[cursor] = 1
                while ( cursor != fwhh['rightmost_hh'] ):
                    cursor = self.get_right_channel ( channel = cursor, profile = profile )
                    multiplier += 1
                    multipliers[cursor] = multiplier
                    fwhh_mask[cursor] = 1
                
                weighted_photon_count = multipliers * profile
                weighted_sum = numpy.sum ( weighted_photon_count )
                fwhh_photon_count = fwhh_mask * profile
                fwhh_photon_count_sum = numpy.sum ( fwhh_photon_count )

                if fwhh_photon_count_sum == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = weighted_sum / fwhh_photon_count_sum

                shifted_center_of_mass = fwhh['leftmost_hh'] - 1 + center_of_mass

                if shifted_center_of_mass != self.cube.max_dep:
                    ordered_shifted_center_of_mass = shifted_center_of_mass % ( self.cube.max_dep )
                
                barycenter_array[row][col] = ordered_shifted_center_of_mass

        return barycenter_array

    def get_fwhh ( self, profile = numpy.ndarray ):
        """
        Returns a dict containing the indices of the FWHH channels in the profile, and the relevant data for FWHH calculation.
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
            
        fwhh_dict = { }
        fwhh_dict['max_height'] = max_height
        fwhh_dict['half_height'] = half_height
        fwhh_dict['max_height_index'] = max_height_index
        fwhh_dict['leftmost_hh'] = leftmost_hh
        fwhh_dict['rightmost_hh'] = rightmost_hh
        fwhh_dict['profile_indices'] = fwhh_profile_indices
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
    fa_barycenter = barycenter_object.run ( )

    print ( " %ds." % ( time ( ) - i_start ) )
    return fa_barycenter
