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
        max_x = cube.shape[1]
        max_y = cube.shape[2]
        max_z = cube.shape[0]
        half_width = floor ( max_z / 2 )

        barycenter_array = numpy.ndarray ( shape = ( max_x, max_y ) )
        multipliers = numpy.ndarray ( shape = ( max_z ) )
        multipliers2 = numpy.ndarray ( shape = ( max_z ) )

        printables = [ x for x in range ( 0, 101, 10 ) ]
        for x in range ( max_x ):
            percentage = int ( 100 * ( x + 1 ) / max_x )
            if ( percentage in printables ):
                self.log ( "Barycenter array calculation: %d%%." % ( percentage ) )
                printables.remove ( percentage )
            for y in range ( max_y ):
                profile = self.__array[:,x,y]
                mass = numpy.sum ( profile )

                first_max_index = numpy.argmax ( profile )
                for z in range ( max_z ):
                    distance = z - first_max_index
                    multipliers2[z] = distance
                    if distance < 0:
                        distance *= -1
                    if distance >= half_width:
                        distance = max_z - distance
                    multipliers[z] = distance
                    #multipliers2[z] = half_width - distance

                weighted_mass = profile * multipliers

                if mass == 0:
                    center_of_mass = 0
                else:
                    center_of_mass = numpy.sum ( weighted_mass ) / mass + first_max_index
                barycenter_array[x][y] = center_of_mass

                target_pixels = [ ( 250, 250 ) ]
                if ( x, y ) in target_pixels:
                    self.log ( profile )
                    self.log ( first_max_index )
                    self.log ( multipliers )
                    self.log ( multipliers2 )
                    self.log ( weighted_mass )
                    self.log ( center_of_mass )

        return barycenter_array

def create_barycenter_array ( array = None ):
    barycenter_object = barycenter ( array = array )
    return barycenter_object.run ( )
