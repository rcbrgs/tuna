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

def create_barycenter_array ( array = None ):
    barycenter_object = barycenter ( array = array )
    return barycenter_object.run ( )
