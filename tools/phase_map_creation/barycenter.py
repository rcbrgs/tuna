from math import floor
import numpy

class spectrum_cube ( object ):
    def __init__ ( self, log = print ):
        super ( spectrum_cube, self ).__init__ ( )
        self.log = log
        self.max_dep = 0
        self.max_row = 0
        self.max_col = 0
        self.channel_range = 0
        self.channel_range_center = 0

class barycenter ( object ):
    def __init__ ( self, array = None, log = print ):
        super ( barycenter, self ).__init__ ( )
        self.log = log

        self.__array = array
        self.cube = spectrum_cube ( )
        self.profile = None
    
    def run_by_central_shifting ( self ):
        """
        Produces a barycenter array from the input array by shifting the spectra, calculating the barycenter and then shifting the result an equal amount.
        """
        self.log ( "Creating barycenter array." )
        if self.__array.ndim != 3:
            return
            
        self.cube.max_dep = self.__array.shape[0]
        self.cube.max_row = self.__array.shape[1]
        self.cube.max_col = self.__array.shape[2]
        self.cube.channel_range = self.cube.max_dep
        self.cube.channel_center = self.cube.max_dep / 2

        barycenter_array = numpy.ndarray ( shape = ( self.cube.max_row, self.cube.max_col ) )
        multipliers = numpy.ndarray ( shape = ( self.cube.max_dep ) )

        for dep in range ( self.cube.max_dep ):
            multipliers[dep] = dep + 1

        test_points = [ ( 2, 464 ) ]

        for row in range ( self.cube.max_row ):
            for col in range ( self.cube.max_col ):
                self.profile = self.__array[:,row,col]
                mass = numpy.sum ( self.profile )
                spectral_regions = self.get_spectral_regions ( array = self.profile )
                peaks_regions = self.get_peaks_regions ( regions_list = spectral_regions )



                apex_position = self.get_apex_index ( peaks_regions = peaks_regions, profile = profile )
                shift = apex_position - center_channel

                shifted_profile = self.shift_profile ( profile = profile, shift = shift )

                weighted_mass = shifted_profile * multipliers

                if mass == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = ( ( numpy.sum ( weighted_mass ) / mass ) + shift - 1 ) % ( max_dep )
                    if center_of_mass == 0:
                        center_of_mass = max_dep
                barycenter_array[row][col] = center_of_mass

                if ( row, col ) in test_points:
                    print ( ">>>>>>>>>>>> position = ( %d, %d ) <<<<<<<<<<<<<<<<<<<" % ( row, col ) )
                    print ( "profile = ", profile )
                    print ( "mass = %d" % mass )
                    print ( "spectral_positions = ", spectral_regions )
                    print ( "peaks_regions = ", peaks_regions )
                    print ( "apex_position = %d" % apex_position )
                    print ( "shift = %d" % shift )
                    print ( "shifted_profile = ", shifted_profile )
                    print ( "weighted_mass = ", weighted_mass )
                    print ( "center_of_mass = %f" % center_of_mass )

        return barycenter_array

    def run_by_central_shifting_and_disconsider_far_away_peaks ( self ):
        """
        Produces a barycenter array from the input array by shifting the spectra, calculating the barycenter and then shifting the result an equal amount.
        """
        self.log ( "Creating barycenter array." )
        if self.__array.ndim != 3:
            return
            
        cube = self.__array
        dep_index = 0
        row_index = 1
        col_index = 2
        max_dep = cube.shape[dep_index]
        max_row = cube.shape[row_index]
        max_col = cube.shape[col_index]
        barycenter_array = numpy.ndarray ( shape = ( max_row, max_col ) )
        center_channel = floor ( max_dep / 2 )
        print ( "center_channel = %d" % center_channel )

        test_points = [ ( 0, 0 ), ( 24, 0 ), ( 24, 256 ), ( 24, 384 ), ( 24, 448 ), ( 24, 480 ), ( 24, 484 ), ( 24, 488 ), ( 24, 492 ), ( 24, 493 ), ( 24, 494 ),  ( 24, 496 ), ( 24, 512 ), ( 232, 270 ), ( 233, 270 ) ]
        test_points = [ ( 93, 127 ), ( 93, 128 ) ]
        test_points = [ ( 3, 460 ) ]
        test_points = [ ( 9, 461 ) ]
        test_points = [ ( 2, 464 ) ]

        for row in range ( max_row ):
            #print ( "row = %d" % row )
            for col in range ( max_col ):
                profile = self.__array[:,row,col]
                mass = numpy.sum ( profile )
                spectral_regions = self.get_regions_list ( array = cube[:,row,col] )
                peaks_regions = self.get_peaks_from_regions ( regions_list = spectral_regions )
                apex_position = self.get_apex_index ( peaks_regions = peaks_regions, profile = profile )
                apex_peak_region_index = self.get_peaks_region ( position = apex_position, peaks_regions = peaks_regions )
                region_to_consider = [apex_position]

                multipliers = numpy.zeros ( shape = ( max_dep ) )
                for dep in range ( max_dep ):
                    if ( dep in region_to_consider ):
                        multipliers[dep] = dep + 1

                shift = apex_position - center_channel

                shifted_profile = self.shift_profile ( profile = profile, shift = shift )

                weighted_mass = shifted_profile * multipliers

                if mass == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = ( ( numpy.sum ( weighted_mass ) / mass ) + shift - 1 ) % ( max_dep )
                    if center_of_mass == 0:
                        center_of_mass = max_dep
                barycenter_array[row][col] = center_of_mass

                if ( row, col ) in test_points:
                    print ( ">>>>>>>>>>>> position = ( %d, %d ) <<<<<<<<<<<<<<<<<<<" % ( row, col ) )
                    print ( "profile = ", profile )
                    print ( "mass = %d" % mass )
                    print ( "spectral_positions = ", spectral_regions )
                    print ( "peaks_regions = ", peaks_regions )
                    print ( "apex_position = %d" % apex_position )
                    print ( "shift = %d" % shift )
                    print ( "shifted_profile = ", shifted_profile )
                    print ( "weighted_mass = ", weighted_mass )
                    print ( "center_of_mass = %f" % center_of_mass )

        return barycenter_array

    def get_peaks_region ( self, position = 0, peaks_regions = [] ):
        for peak in range ( len ( peaks_regions ) ):
            if ( position > peaks_regions[peak][0] and
                 position < peaks_regions[peak][1] ):
                return peak
        return len ( peaks_regions ) - 1

    def shift_profile ( self, profile = numpy.ndarray, shift = 0 ):
        """
        Shifts a profile a given number of channels, positive values shift channel positions in the profile to the right.
        """
        if profile is not None:
            if ( shift != 0 and
                 shift != profile.shape[0] ):
                shift_index = ( abs ( profile.shape[0] + shift ) ) % profile.shape[0]
                profile_left = profile[0:shift]
                profile_right = profile[shift:profile.shape[0]]
                return numpy.concatenate ( ( profile_right, profile_left ) )
            else:
                return profile

    def get_finite_differences_1D ( self, array = None ):
        """
        Produces an array with the same shape as the input, but where each element is the difference between its value and the previous one. The first element of the output is equal to the difference between the first and last elements.
        
        Parameters
        ---
        array -- 1D numpy ndarray
        """
        max_dep = array.shape[0]
        mass = numpy.sum ( array )
        peak = numpy.max ( array )
        differences = numpy.ndarray ( shape = ( max_dep ) )
        differences[0] = ( array[0] - array[max_dep - 1] )
        for dep in range ( 1, max_dep ):
            differences[dep] = array[dep] - array[dep - 1]
        return differences

    def get_spectral_regions ( self, array = None ):
        """
        Produces a dict containing keys:
        region_signal, region_start_index, region_end_index, region_mass
        Where region_signal is 1 if the finite differences are positive, -1 if negative and 0 if 0.
        region_mass is the amount of signal in the channels contained in the region.

        Parameters
        ---
        array -- 1D numpy ndarray
        """
        differences = self.get_finite_differences_1D ( array = array )
        max_dep = array.shape[0]
        # produce list of finite differences' signals
        derivative_signal = numpy.zeros ( shape = ( max_dep ), dtype = numpy.int16 )
        for dep in range ( max_dep ):
            if differences[dep] > 0:
                derivative_signal[dep] = 1
            elif differences[dep] < 0:
                derivative_signal[dep] = -1
        # produce regions list, without mass
        regions_list = []
        region_start = 0
        region_end = 0
        region_signal = derivative_signal[0]
        for dep in range ( 1, max_dep ):
            if ( derivative_signal[dep] == region_signal ):
                region_end = dep
            else:
                regions_list.append ( ( region_signal, region_start, region_end ) )
                region_signal = derivative_signal[dep]
                region_start = dep
                region_end = dep
            if ( dep == max_dep - 1 ):
                regions_list.append ( ( region_signal, region_start, region_end ) )


        end_list = len ( regions_list ) - 1
        # if the first and final regions hav ethe same signal, merge both
        if regions_list[0][0] == regions_list[end_list][0]:
            region_signal = regions_list[0][0]
            region_start = regions_list[end_list][1]
            region_end = regions_list[0][2]
            regions_list.pop ( end_list )
            if ( len ( regions_list ) > 0 ):
                regions_list.pop ( 0 )
            regions_list.append ( ( region_signal, region_start, region_end ) )
        # include the mass of each region
        result_list = [ ]
        for region in regions_list:
            result_dict = { }
            region_mass = 0

            if ( region[1] <= region[2] ):
                channel_start = region[1]
                channel_end = region[2] + 1
                for channel in range ( channel_start, channel_end ):
                    region_mass += array[channel]

            else:
                left_end = region[2]
                right_start = region[1]
                for channel in range ( left_end + 1 ):
                    region_mass += array[channel]
                for channel in range ( right_start, array.shape[0] ):
                    region_mass += array[channel]

            result_dict['finite_difference_signal'] = region[0]
            result_dict['profile_start_index'] = region[1]
            result_dict['profile_end_index'] = region[2]
            result_dict['mass'] = region_mass
            result_list.append ( result_dict )
        return result_list

    def get_regions_list ( self, array = None ):
        """
        Produces an unsorted list containing tuples of the form:
        ( region_signal, region_start_index, region_end_index, region_mass )
        Where region_signal is 1 if the finite differences are positive, -1 if negative and 0 if 0.
        region_mass is the amount of signal in the channels contained in the region.

        Parameters
        ---
        array -- 1D numpy ndarray
        """
        differences = self.get_finite_differences_1D ( array = array )
        max_dep = array.shape[0]
        # produce list of finite differences' signals
        derivative_signal = numpy.zeros ( shape = ( max_dep ), dtype = numpy.int16 )
        for dep in range ( max_dep ):
            if differences[dep] > 0:
                derivative_signal[dep] = 1
            elif differences[dep] < 0:
                derivative_signal[dep] = -1
        # produce regions list, without mass
        regions_list = []
        region_start = 0
        region_end = 0
        region_signal = derivative_signal[0]
        for dep in range ( 1, max_dep ):
            if ( derivative_signal[dep] == region_signal ):
                region_end = dep
            else:
                regions_list.append ( ( region_signal, region_start, region_end ) )
                region_signal = derivative_signal[dep]
                region_start = dep
                region_end = dep
            if ( dep == max_dep - 1 ):
                regions_list.append ( ( region_signal, region_start, region_end ) )


        end_list = len ( regions_list ) - 1
        # if the first and final regions hav ethe same signal, merge both
        if regions_list[0][0] == regions_list[end_list][0]:
            region_signal = regions_list[0][0]
            region_start = regions_list[end_list][1]
            region_end = regions_list[0][2]
            regions_list.pop ( end_list )
            if ( len ( regions_list ) > 0 ):
                regions_list.pop ( 0 )
            regions_list.append ( ( region_signal, region_start, region_end ) )
        # include the mass of each region
        result = []
        for region in regions_list:
            region_mass = 0

            if ( region[1] <= region[2] ):
                channel_start = region[1]
                channel_end = region[2] + 1
                for channel in range ( channel_start, channel_end ):
                    region_mass += array[channel]

            else:
                left_end = region[2]
                right_start = region[1]
                for channel in range ( left_end + 1 ):
                    region_mass += array[channel]
                for channel in range ( right_start, array.shape[0] ):
                    region_mass += array[channel]

            result.append ( ( region[0], region[1], region[2], region_mass ) )
        return result

    def get_peaks_from_regions_old ( self, regions_list = [] ):
        """
        Produces a peak list from the regions list.
        Peaks must have the following patterns concerning their and their neighbours' finite differences:
        +-
        +=-

        Parameters:
        ---
        regions_list -- list of tuples of type ( region_signal, region_start_index, region_end_index, region_mass )
        """
        peaks_list = []
        for region in range ( len ( regions_list ) ):
            next_region = ( region + 1 ) % len ( regions_list )
            next_next_region = ( region + 2 ) % len ( regions_list )
            if regions_list[region][0] == 1:
                if ( regions_list[next_region][0] == 0 and
                     regions_list[next_next_region][0] == -1 ):
                    peaks_list.append ( ( regions_list[region][1], regions_list[next_next_region][2], regions_list[region][3] + regions_list[next_next_region][3] ) )
                elif ( regions_list[next_region][0] == -1 ):
                    peaks_list.append ( ( regions_list[region][1], regions_list[next_region][2], ( regions_list[region][3] + regions_list[next_region][3] ) ) )
        return peaks_list

    def get_peaks_from_regions ( self, regions_list = [] ):
        """
        Produces a peak list from the regions list.
        Peaks must have the following patterns concerning their and their neighbours' finite differences:
        +-
        +=-

        Parameters:
        ---
        regions_list -- list of tuples of type ( region_signal, region_start_index, region_end_index, region_mass )
        """
        peaks_list = []
        for region in range ( len ( regions_list ) ):
            if regions_list[region][0] == 1:
                next_region = ( region + 1 ) % len ( regions_list )
                next_next_region = ( region + 2 ) % len ( regions_list )
                if ( regions_list[next_region][0] == 0 and
                     regions_list[next_next_region][0] == -1 ):
                    peak_start = regions_list[region][1]
                    peak_end = regions_list[next_next_region][2]
                    peak_mass = ( regions_list[region][3] +
                                  regions_list[next_region][3] +
                                  regions_list[next_next_region][3] )
                    peaks_list.append ( ( peak_start, peak_end, peak_mass ) )
                elif ( regions_list[next_region][0] == -1 ):
                    peak_start = regions_list[region][1]
                    peak_end = regions_list[next_region][2]
                    peak_mass = ( regions_list[region][3] + 
                                  regions_list[next_region][3] )
                    peaks_list.append ( ( peak_start, peak_end, peak_mass ) )
        return peaks_list

    def get_peaks_regions ( self, regions_list = [] ):
        """
        Produces a peak list from the regions list.
        Peaks must have the following patterns concerning their and their neighbours' finite differences:
        +-
        +=-

        Parameters:
        ---
        regions_list -- list of tuples of type ( region_signal, region_start_index, region_end_index, region_mass )
        """
        peaks_list = []
        for region in range ( len ( regions_list ) ):
            if regions_list[region]['finite_difference_signal'] == 1:
                next_region = ( region + 1 ) % len ( regions_list )
                next_next_region = ( region + 2 ) % len ( regions_list )
                if ( regions_list[next_region]['finite_difference_signal'] == 0 and
                     regions_list[next_next_region]['finite_difference_signal'] == -1 ):
                    peak_start = regions_list[region]['profile_start_index']
                    peak_end = regions_list[next_next_region]['profile_end_index']
                    peak_mass = ( regions_list[region]['mass'] +
                                  regions_list[next_region]['mass'] +
                                  regions_list[next_next_region]['mass'] )
                    peaks_list.append ( ( peak_start, peak_end, peak_mass ) )
                elif ( regions_list[next_region]['finite_difference_signal'] == -1 ):
                    peak_start = regions_list[region]['profile_start_index']
                    peak_end = regions_list[next_region]['profile_end_index']
                    peak_mass = ( regions_list[region]['mass'] + 
                                  regions_list[next_region]['mass'] )
                    peaks_list.append ( ( peak_start, peak_end, peak_mass ) )
        return peaks_list

    def find_start_index ( self, regions_list = [] ):
        """
        Determines where is the left shoulder of the most massive peak of the spectra.
        
        Parameters:
        ---
        regions_list -- list of tuples of the type ( region_signal, region start_index, region_end_index )
        """
        peaks_list = self.get_peaks_from_regions ( regions_list = regions_list )
        if ( peaks_list == [] ):
            return 0
        #print ( peaks_list ) 
        peaks_masses = numpy.ndarray ( shape = len ( peaks_list ) )
        for peak in range ( len ( peaks_list ) ):
            peaks_masses[peak] = peaks_list[peak][2]
        most_massive_peak = numpy.argmax ( peaks_masses )
#        print ( most_massive_peak )
#        print ( peaks_list )
        return peaks_list[most_massive_peak][0]

    def get_apex_index ( self, peaks_regions = [], profile = numpy.ndarray ):
        """
        Determines where is the center of the most massive peak of the spectra.
        
        Parameters:
        ---
        peaks_regions -- list of tuples of the type ( region start_index, region_end_index, region_mass )
        """
        if peaks_regions == []:
            return 0
        peaks_masses = numpy.ndarray ( shape = ( len ( peaks_regions ) ) )
        for peak in range ( len ( peaks_regions ) ):
            peaks_masses[peak] = peaks_regions[peak][2]
        #print ( "peaks_masses = ", peaks_masses )
        most_massive_peak = numpy.argmax ( peaks_masses )
        #print ( "most_massive_peak = %d" % most_massive_peak )
        apex_region_start_index = peaks_regions[most_massive_peak][0]
        #print ( "apex_region_start_index = %d" % apex_region_start_index )
        apex_region_end_index = peaks_regions[most_massive_peak][1]
        #print ( "apex_region_end_index = %d" % apex_region_end_index )

        def get_argmax_from_wrapped_range ( start_index = 0, end_index = 0, profile = [] ):
            if start_index <= end_index:
                auxiliary = profile[start_index:end_index]
                auxiliary_argmax = numpy.argmax ( auxiliary )
                return auxiliary_argmax + start_index
            else:
                auxiliary_left = profile[start_index:]
                auxiliary_right = profile[:end_index]
                auxiliary = numpy.concatenate ( ( auxiliary_left, auxiliary_right ) )
                auxiliary_argmax =  numpy.argmax ( auxiliary )
                return ( auxiliary_argmax + start_index ) % len ( profile )

        argmax = get_argmax_from_wrapped_range ( start_index = apex_region_start_index,
                                                 end_index = apex_region_end_index,
                                                 profile = profile )
        
        #print ( "argmax = %d" % argmax )
        return argmax

def create_barycenter_array ( array = None ):
    barycenter_object = barycenter ( array = array )
    #return barycenter_object.run_by_central_shifting ( )
    return barycenter_object.run_by_central_shifting_and_disconsider_far_away_peaks ( )
