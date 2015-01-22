from math import floor
import numpy

class barycenter ( object ):
    def __init__ ( self, array = None, log = print ):
        super ( barycenter, self ).__init__ ( )
        self.__array = array
        self.log = log
    
    def run ( self ):
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
        multipliers = numpy.ndarray ( shape = ( max_dep ) )

        for dep in range ( max_dep ):
            multipliers[dep] = dep + 1

        for row in range ( max_row ):
            for col in range ( max_col ):
                profile = self.__array[:,row,col]
                mass = numpy.sum ( profile )
                first_min_index = numpy.argmin ( profile )
                if ( first_min_index != 0 ):
                    shifted_profile_right = profile[first_min_index:]
                    shifted_profile_left  = profile[:first_min_index]
                else:
                    shifted_profile_left = profile
                    shifted_profile_right = []
                    
                shifted_profile = numpy.concatenate ( ( shifted_profile_right, shifted_profile_left ) )

                weighted_mass = shifted_profile * multipliers

                if mass == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = ( ( numpy.sum ( weighted_mass ) / mass ) + first_min_index - 1 ) % max_dep
                    if center_of_mass == 0:
                        center_of_mass = max_dep
                barycenter_array[row][col] = center_of_mass

        return barycenter_array

    def run2 ( self ):
        """
        Produces a barycenter array from the input array. Will do so by shifting the spectra so that the geometric center of the 3 contiguous regions containing the most mass is the geometric center of the shifted spectra.
        The idea behind this is: considering the possible "profiles" of the spectra, the "central line" will be either near a single isolated peak, or near the valley between two peaks. 
        Also a peak's finite differences should have the following patterns: + - or + = -, so only consecutive regions with these profiles are considered as candidates.
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
        multipliers = numpy.ndarray ( shape = ( max_dep ) )

        for dep in range ( max_dep ):
            multipliers[dep] = dep + 1

        for row in range ( max_row ):
            print ( "row = %d" % row )
            for col in range ( max_col ):
                profile = self.__array[:,row,col]
                mass = numpy.sum ( profile )
                spectral_regions = self.get_regions_list ( array = cube[:,row,col] )
                first_min_index = self.find_start_index ( spectral_regions )
                if ( first_min_index != 0 ):
                    shifted_profile_right = profile[first_min_index:]
                    shifted_profile_left  = profile[:first_min_index]
                else:
                    shifted_profile_left = profile
                    shifted_profile_right = []
                    
                shifted_profile = numpy.concatenate ( ( shifted_profile_right, shifted_profile_left ) )

                weighted_mass = shifted_profile * multipliers

                if mass == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = ( ( numpy.sum ( weighted_mass ) / mass ) + first_min_index - 1 ) % max_dep
                    if center_of_mass == 0:
                        center_of_mass = max_dep
                barycenter_array[row][col] = center_of_mass

        return barycenter_array

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
                if dep == max_dep - 1:
                    regions_list.append ( ( region_signal, region_start, region_end ) )
            else:
                regions_list.append ( ( region_signal, region_start, region_end ) )
                region_signal = derivative_signal[dep]
                region_start = dep
                region_end = dep

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
        # produce a final list including the mass of each region
        result = []
        for region in regions_list:
            region_mass = 0
            for channel in range ( region[1], region[2] + 1 ):
                region_mass += array[channel]
            result.append ( ( region[0], region[1], region[2], region_mass ) )
        return result

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
            next_region = ( region + 1 ) % len ( regions_list )
            next_next_region = ( region + 2 ) % len ( regions_list )
            if regions_list[region][0] == 1:
                if ( regions_list[next_region][0] == 0 and
                     regions_list[next_next_region][0] == -1 ):
                    peaks_list.append ( ( regions_list[region][1], regions_list[next_next_region][2], regions_list[region][3] + regions_list[next_next_region][3] ) )
                elif ( regions_list[next_region][0] == -1 ):
                    peaks_list.append ( ( regions_list[region][1], regions_list[next_region][2], ( regions_list[region][3] + regions_list[next_region][3] ) ) )
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

#    def remove_continuum_from_spectra ( self, array = None ):
#        filtered_spectra = array
#        mass = numpy.sum ( array )
#        significance = 1
#
#        while ( significance == 1 ):
#            minimum = numpy.argmin ( filtered_spectra )
#            filtered_spectra_left = filtered_spectra[:minimum]
#            filtered_spectra_right = filtered_spectra[minimum+1:]
#            filtered_spectra = numpy.concatenate ( ( filtered_spectra_left, filtered_spectra_right ) )
#            new_mass = numpy.sum ( filtered_spectra )
#            significance = new_mass / mass
#
#        print ( "Pixel spectra significance after continuum removal = %f" % significance )
#        
#        return filtered_spectra

def create_barycenter_array ( array = None ):
    test_row = 220
    test_column = 220
    barycenter_object = barycenter ( array = array )
    #test_differences = barycenter_object.get_finite_differences_1D ( array = array[:,test_row,test_column] )
    #test_filter = barycenter_object.remove_continuum_from_spectra ( array = array[:,test_row,test_column] )
    #for row in range ( test_row - 1, test_row + 2 ):
    #    print ( " row %d: " % row )
    #    print ( array[:,row,test_column] )
    #    test_regions_list = barycenter_object.get_regions_list ( array[:,row,test_column] )
    #    print ( test_regions_list ) 
    #    left_shoulder = barycenter_object.find_start_index ( test_regions_list )
    #    print ( left_shoulder )
    return barycenter_object.run2 ( )
