from math import floor
import numpy

class spectrum_cube ( object ):
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
    def __init__ ( self, array = None, log = print ):
        super ( barycenter, self ).__init__ ( )
        self.log = log

        self.__array = array
        self.__number_of_spectral_regions_array = None
        self.__photon_counts_array = None
        self.__number_spectral_peaks_array = None
        self.cube = spectrum_cube ( )
        self.profile = None
    
    def run ( self ):
        """
        Produces a barycenter array from the input array by shifting the spectra, calculating the barycenter and then shifting the result an equal amount.
        """
        self.log ( "Creating barycenter array." )
        if self.__array.ndim != 3:
            return
            
        self.cube.max_dep = self.__array.shape[self.cube.dep_index]
        self.cube.max_row = self.__array.shape[self.cube.row_index]
        self.cube.max_col = self.__array.shape[self.cube.col_index]
        barycenter_array = numpy.ndarray ( shape = ( self.cube.max_row, self.cube.max_col ) )
        center_channel = floor ( self.cube.max_dep / 2 )
        print ( "center_channel = %d" % center_channel )

        test_points = [ ( 0, 0 ) ] # first pixel of first row
        test_points.append ( ( 0, 184 ) ) # 35.904 (on the first ring border)
        test_points.append ( ( 93, 128 ) ) # has peak on central channel => no shift
        test_points.append ( ( 114, 240 ) ) # 35.984 (on the central circle border)
        test_points.append ( ( 256, 0 ) ) # first pixel on central row
        test_points.append ( ( 512, 0 ) ) # first pixel in last row

        self.__number_of_spectral_regions_array = numpy.zeros ( shape = ( self.cube.max_row, self.cube.max_col ) )
        self.__photon_counts_array = numpy.zeros ( shape = ( self.cube.max_row, self.cube.max_col ) )
        self.__number_of_spectral_peaks_array = numpy.zeros ( shape = ( self.cube.max_row, self.cube.max_col ) )

        for row in range ( self.cube.max_row ):
            for col in range ( self.cube.max_col ):
                profile = self.__array[:,row,col]
                mass = numpy.sum ( profile )
                self.__photon_counts_array[row][col] = mass
                spectral_regions = self.get_spectral_regions ( array = profile )
                self.__number_of_spectral_regions_array[row][col] = len ( spectral_regions )
                peaks = self.get_peaks ( regions = spectral_regions )
                self.__number_of_spectral_peaks_array[row][col] = len ( peaks )
                apex = self.get_apex ( peaks = peaks, profile = profile )
                apex_peak = self.get_peak_from_position ( position = apex, peaks = peaks )
                peaks_to_consider = [apex_peak]
                # missing: to consider neighbour peaks
                positions_to_consider = [ ]
                for peak in peaks_to_consider:
                    positions_to_consider += peaks[peak]['profile_indices']
                
                multipliers = numpy.zeros ( shape = ( self.cube.max_dep ) )
                interest_mask = numpy.zeros ( shape = ( self.cube.max_dep ) )
                continuum_channels = self.cube.max_dep
                for dep in range ( self.cube.max_dep ):
                    multipliers[dep] = dep + 1
                    if ( dep in positions_to_consider ):
                        interest_mask[dep] = 1
                        continuum_channels -= 1

                shift = apex - center_channel

                interest_mask = self.shift_profile ( profile = interest_mask, shift = shift )

                shifted_profile = self.shift_profile ( profile = profile, shift = shift )

                # continuum
                continuum = numpy.zeros ( shape = ( self.cube.max_dep ) )
                continuum = shifted_profile - shifted_profile * interest_mask
                if ( continuum_channels == 0 ):
                    average_continuum = 0
                else:
                    average_continuum = numpy.sum ( continuum ) / continuum_channels
                for dep in range ( self.cube.max_dep ):
                    continuum[dep] = average_continuum

                weighted_mass = interest_mask * multipliers * ( shifted_profile - continuum )

                if mass == 0:
                    shifted_center_of_mass = 0
                else:
                    shifted_center_of_mass = numpy.sum ( weighted_mass ) / mass

                center_of_mass = abs ( shifted_center_of_mass + shift ) % ( self.cube.max_dep )
                
                #barycenter_array[row][col] = shifted_center_of_mass
                barycenter_array[row][col] = center_of_mass

                if ( row, col ) in test_points:
                    print ( ">>>>>>>>>>>> position = ( %d, %d ) <<<<<<<<<<<<<<<<<<<" % ( row, col ) )
                    print ( "profile = ", profile )
                    print ( "mass = %d" % mass )
                    print ( "spectral_regions = " )
                    #for spectrum in spectral_regions:
                    #    print ( spectrum )
                    print ( "peaks = " )
                    for peak in peaks:
                        print ( peak )
                    print ( "apex_position = %d" % apex )
                    print ( "peaks_to_consider = ", peaks_to_consider )
                    print ( "positions_to_consider = ", positions_to_consider )
                    print ( "multipliers = ", multipliers )
                    print ( "interest_mask = ", interest_mask )
                    print ( "shift = %d" % shift )
                    print ( "shifted_profile = ", shifted_profile )
                    print ( "average_continuum = %f" % average_continuum )
                    print ( "weighted_mass = ", weighted_mass )
                    print ( "shifted_center_of_mass = %f" % shifted_center_of_mass )
                    print ( "center_of_mass = %f" % center_of_mass )

        return barycenter_array

    def get_peak_from_position ( self, position = 0, peaks = [] ):
        if peaks == [ ]:
            return 0
        for peak in range ( len ( peaks ) - 1 ):
            if ( position >= peaks[peak]['profile_start_index'] and
                 position <= peaks[peak]['profile_end_index'] ):
                return peak
        return len ( peaks ) - 1

    def get_apex ( self, peaks = [], profile = numpy.ndarray ):
        """
        Determines where is the center of the most massive peak of the spectra.
        
        Parameters:
        ---
        peaks_regions -- list of tuples of the type ( region start_index, region_end_index, region_mass )
        """
        if peaks == []:
            return 0
        peaks_masses = numpy.ndarray ( shape = ( len ( peaks ) ) )
        for peak in range ( len ( peaks ) ):
            peaks_masses[peak] = peaks[peak]['mass']
        most_massive_peak = numpy.argmax ( peaks_masses )
        apex_region_start_index = peaks[most_massive_peak]['profile_start_index']
        apex_region_end_index = peaks[most_massive_peak]['profile_end_index']

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
        
        return argmax

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



    def get_peaks ( self, regions = [] ):
        """
        Produces a peak list from the regions list.
        Peaks must have the following patterns concerning their and their neighbours' finite differences:
        =   ( only when the signal is constant )
        +-
        +=-
        =+-
        =+-=
        =+=-
        =+=-=

        Parameters:
        ---
        regions_list -- list of dicts with keys ( finite_difference_signal, profile_start_index, profile_end_index, mass )
        """

        def find_left_shoulder ( regions_list = [ ], position = 0 ):
            """
            Supposing position is a region of positive signal, the left shoulder is 
            the first previous region of negative signal.
            """
            shoulder = position
            for entry in range ( position ):
                if regions_list[entry]['finite_difference_signal'] == -1:
                    shoulder = entry
            if shoulder == position:
                for entry in range ( position, len ( regions_list ) ):
                    if regions_list[entry]['finite_difference_signal'] == -1:
                        shoulder = entry
                        break
            return shoulder

        def find_right_shoulder ( regions_list = [ ], position = 0 ):
            """ 
            Supposing position is a region of positive signal, the right shoulder is
            at the first next positive region.
            """
            shoulder = position
            for entry in range ( position, len ( regions_list ) ):
                if regions_list[entry]['finite_difference_signal'] == 1:
                    shoulder = entry
            if shoulder == position:
                for entry in range ( position ):
                    if regions_list[entry]['finite_difference_signal'] == 1:
                        shoulder = entry
                        break
            return shoulder

        possibilities = [ ]
        for entry in range ( len ( regions ) ):
            if regions[entry]['finite_difference_signal'] == 1:
                possibilities.append ( entry )

        peaks_list = [ ]
        for next_positive in possibilities:
            left = find_left_shoulder ( regions_list = regions, position = next_positive )
            right = find_right_shoulder ( regions_list = regions, position = next_positive )

            peak_dict = { }
            peak_dict['profile_start_index'] = regions[left]['profile_start_index']
            peak_dict['profile_end_index'] = regions[right]['profile_end_index']

            if left <= right:
                peak_regions_list = [ element for element in range ( left, right ) ]
                if right == len ( regions ):
                    peak_regions_list.append ( 0 )
                else:
                    peak_regions_list.append ( right )
            else:
                left_aux_list = [ element for element in range ( right + 1 ) ]
                right_aux_list = [ element for element in range ( left, len ( regions ) ) ]
                peak_regions_list = left_aux_list + right_aux_list

            peak_dict['profile_indices'] = [ ]
            for element in peak_regions_list:
                for entry in regions[element]['profile_indices']:
                    peak_dict['profile_indices'].append ( entry )

            mass = 0
            for element in peak_regions_list:
                mass += regions[element]['mass']
            peak_dict['mass'] = mass
            peaks_list.append ( peak_dict )

        if peaks_list == [ ]:
            peak_dict = { }
            peak_dict['profile_start_index'] = 0
            peak_dict['profile_end_index'] = self.cube.max_dep - 1
            peak_dict['mass'] = 0
            peak_dict['profile_indices'] = range ( self.cube.max_dep )
            peaks_list.append ( peak_dict )
        return peaks_list

    def get_peaks_old ( self, regions = [] ):
        """
        Produces a peak list from the regions list.
        Peaks must have the following patterns concerning their and their neighbours' finite differences:
        +-
        +=-
        Not yet implemented:
        =+-
        =+-=
        =+=-
        =+=-=

        Parameters:
        ---
        regions_list -- list of dicts with keys ( finite_difference_signal, profile_start_index, profile_end_index, mass )
        """
        peaks_list = []
        for region in range ( len ( regions ) ):
            if regions[region]['finite_difference_signal'] == 1:
                next_region = ( region + 1 ) % len ( regions )
                next_next_region = ( region + 2 ) % len ( regions )
                peak_dict = { }
                if ( regions[next_region]['finite_difference_signal'] == 0 and
                     regions[next_next_region]['finite_difference_signal'] == -1 ):
                    peak_start = regions[region]['profile_start_index']
                    peak_end = regions[next_next_region]['profile_end_index']
                    peak_mass = ( regions[region]['mass'] +
                                  regions[next_region]['mass'] +
                                  regions[next_next_region]['mass'] )
                    peak_dict['profile_start_index'] = peak_start
                    peak_dict['profile_end_index'] = peak_end
                    peak_dict['mass'] = peak_mass
                    peak_dict['profile_indices'] = ( regions[region]['profile_indices'] +
                                                     regions[next_region]['profile_indices'] +
                                                     regions[next_next_region]['profile_indices'] )
                    peaks_list.append ( peak_dict )
                elif ( regions[next_region]['finite_difference_signal'] == -1 ):
                    peak_start = regions[region]['profile_start_index']
                    peak_end = regions[next_region]['profile_end_index']
                    peak_mass = ( regions[region]['mass'] + 
                                  regions[next_region]['mass'] )
                    peak_dict['profile_start_index'] = peak_start
                    peak_dict['profile_end_index'] = peak_end
                    peak_dict['mass'] = peak_mass
                    peak_dict['profile_indices'] = ( regions[region]['profile_indices'] +
                                                     regions[next_region]['profile_indices'] )
                    peaks_list.append ( peak_dict )

        if peaks_list == [ ]:
            peak_dict = { }
            peak_dict['profile_start_index'] = 0
            peak_dict['profile_end_index'] = self.cube.max_dep - 1
            peak_dict['mass'] = 0
            peak_dict['profile_indices'] = range ( self.cube.max_dep )
            peaks_list.append ( peak_dict )
        return peaks_list

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
        regions_list = [ ]
        region_start = 0
        region_end = 0
        region_signal = derivative_signal[0]
        region_indices = [ 0 ]
        for dep in range ( 1, max_dep ):
            if ( derivative_signal[dep] == region_signal ):
                region_end = dep
                region_indices.append ( dep )
            else:
                regions_list.append ( ( region_signal, region_start, region_end, region_indices ) )
                region_signal = derivative_signal[dep]
                region_start = dep
                region_end = dep
                region_indices = [ dep ]
            if ( dep == max_dep - 1 ):
                regions_list.append ( ( region_signal, region_start, region_end, region_indices ) )


        end_list = len ( regions_list ) - 1
        # if the first and final regions have the same signal, merge both
        if regions_list[0][0] == regions_list[end_list][0]:
            region_signal = regions_list[0][0]
            region_start = regions_list[end_list][1]
            region_end = regions_list[0][2]
            merged_indices = regions_list[0][3] + regions_list[end_list][3]
            regions_list.pop ( end_list )
            if ( len ( regions_list ) > 0 ):
                regions_list.pop ( 0 )
            regions_list.append ( ( region_signal, region_start, region_end, merged_indices ) )
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
            result_dict['profile_indices'] = region[3]
            result_list.append ( result_dict )
        return result_list

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

    def get_number_of_spectral_regions_array ( self ):
        return self.__number_of_spectral_regions_array

    def get_photon_counts_array ( self ):
        return self.__photon_counts_array

    def get_number_of_spectral_peaks_array ( self ):
        return self.__number_of_spectral_peaks_array

def create_barycenter_array ( array = None ):
    barycenter_object = barycenter ( array = array )
    #return barycenter_object.run_by_central_shifting ( )
    return barycenter_object.run ( )
