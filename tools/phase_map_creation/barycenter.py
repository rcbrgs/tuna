import numpy

class barycenter ( object ):
    def __init__ ( self, array = None, log = print ):
        super ( barycenter, self ).__init__ ( )
        self.__array = array
        self.log = log
    
    def run ( self ):
        if self.__array.ndim != 3:
            return
            
        cube = self.__array

        max_x = cube.shape[1]
        max_y = cube.shape[2]
        max_z = cube.shape[0]
        barycenter_array = numpy.ndarray ( shape = ( max_x, max_y ) )

        for x in range ( max_x ):
            self.log ( "Column %d." % ( x ) )
            for y in range ( max_y ):
                profile = self.__array[:,x,y]
                center_of_mass = 0.0
                mass = 0.0
                for z in range ( max_z ):
                    center_of_mass += profile[z] * ( z + 1 )
                    mass += profile[z]
                center_of_mass /= mass
                barycenter_array[x][y] = center_of_mass

        print ( barycenter_array )
        return barycenter_array

def create_barycenter_array ( array = None ):
    barycenter_object = barycenter ( array = array )
    return barycenter_object.run ( )
