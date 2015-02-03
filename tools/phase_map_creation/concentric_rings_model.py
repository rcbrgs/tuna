"""
This model corresponds to the idea that a Fabry-Perot data file should consist of concentric rings of homogeneous values.
This will not be exact because of noise. Therefore, if we are able to fit the model to most of a data file, the parts that do not fit well might be noise.
"""

import numpy

#class ring ( object ):
#    """
#    Representation of an individual ring in a FP image.
#    """
#    def __init__ ( self, array, center, spectral_value, spectral_value_uncertainty )
#        super ( ring, self ).__init__ ( )
#        self.__array = array
#        self.__center = center
#        self.__spectral_value = spectral_value
#        self.__spectral_value_uncertainty = spectral_value_uncertainty
#        
#    def set_array ( self, array = numpy.ndarray ):
#        self.__array = array#
#
#def create_ring_array ( array, spectral_value, spectral_value_uncertainty ):
#    ring_array = numpy.zeros ( shape = array.shape, dtype = numpy.int16 )
#    for row in range ( array.shape[0] ):
#        for col in range ( array.shape[1] ):
#            if ( array[row][col] >= spectral_value - spectral_value_uncertainty and
#                 array[row][col] <= spectral_value + spectral_value_uncertainty ):
#                ring_array = 1
#    ring ( array = ring_array, spectral_value = 

def find_concentric_rings ( array = numpy.ndarray ):
    row_max = array.shape[0]
    col_max = array.shape[1]
    # find center: find distinct values
    distinct_values = [ element for element in range ( int ( numpy.amax ( array ) ) + 1 ) ]
    print ( distinct_values )
    # find center: find per-value medians
    per_value_centers = { }
    for element in distinct_values:
        per_value_entry = { }
        per_value_entry['sum'] = ( 0, 0 )
        per_value_entry['pixels'] = 0
        per_value_centers[element] = per_value_entry
    for row in range ( row_max ):
        for col in range ( col_max ):
            value = int ( array[row][col] )
            new_tuple = ( per_value_centers[value]['sum'][0] + row,
                          per_value_centers[value]['sum'][1] + col )
            per_value_centers[value]['sum'] = new_tuple
            per_value_centers[value]['pixels'] += 1
    for element in distinct_values:
        print ( "Center for channel %d, %d pixels: ( %f, %f )." % ( element, 
                                                                    per_value_centers[element]['pixels'],
                                                                    int ( per_value_centers[element]['sum'][0] / per_value_centers[element]['pixels'] ),
                                                                    int ( per_value_centers[element]['sum'][1] / per_value_centers[element]['pixels'] ) ) )
    

    #for row in range ( row_max ):
    #    for col in range ( col_max ):
    #        if array[row][col] not in distinct_values:
    #            distinct_values.append ( array[row][col] )
    
    
    # find rings around center
    
