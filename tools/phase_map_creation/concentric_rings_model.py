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

def get_free_spectral_range( array = numpy.ndarray ):
    """
    A quick-and-dirty way to measure the free range in FP units.
    The method subtracts each frame of the data-cube from the
    first one. Then, it calculates the absolute value and collapse
    in X and Y. The FSR is where the resulting spectrum is minimum,
    excluding (of course), the first one.
    Originally written by Bruno Quint, adapted by Renato Borges.
    """

    print ( " Finding the free-spectral-range." )

    # First frame is the reference frame
    ref_frame = array[0,:,:]

    # Subtract all frames from the first frame
    data = array - ref_frame

    # Get the absolute value
    data = numpy.abs ( data )

    # Sum over the spatial directions
    data = data.sum ( axis = 2 )
    data = data.sum ( axis = 1 )

    # Interpolate data
    il_depth = numpy.arange ( array.shape[0] )
    s = interpolate.UnivariateSpline ( il_depth, data, k = 3 )
    z = numpy.linspace ( il_depth[5:].min ( ), il_depth.max ( ), 1000 )

    # Find the free-spectral-range in z units
    fsr = z[numpy.argmin ( s ( z ) )] - il_depth[0]

    # Find the free-spectral-range in number of channels
    fsr_channel = numpy.argmin ( numpy.abs ( il_depth - z[numpy.argmin ( s ( z ) ) ] ) )

    # Calculate the sampling
    sampling = fsr / fsr_channel

    units = "channels"
    print( "FSR = %.1f %s" % ( fsr, units ) )
    print( "    = %d channels" % fsr_channel )
    print( "Sampling = %.1f %s / channel" % ( sampling, units ) )

    return fsr

def find_concentric_rings_center ( array = numpy.ndarray ):
    """
    Function used to find the center of the rings inside a FP data-cube.
    Originally developed by Bruno Quint, for phmxtractor.py, adapted by Renato Borges for Tuna.
    """

    #from __future__ import division, print_function
    #import argparse
    #import astropy.io.fits as pyfits
    import matplotlib.pyplot as pyplot
    #import numpy
    #import time
    #import scipy
    #import scipy.interpolate as interpolate
    #import scipy.ndimage as ndimage
    #import sys

    #now = time.time()

    # Renaming some variables
    width = array.shape[0]
    height = array.shape[1]
    #fsr = round(self.free_spectral_range / self.header['C3_3'])

    # Choosing the points
    x = ( numpy.linspace ( 0.2, 0.8, 500 ) * width ).astype ( int )
    y = ( numpy.linspace ( 0.2, 0.8, 500 ) * height ).astype ( int )

    ref_x = width / 2
    ref_y = height / 2

    self.log ( "Start center finding." )
    old_ref_x = ref_x
    old_ref_y = ref_y

    #if self.show:
        #pyplot.figure()

    for i in range ( 6 ):
        ref_y = max ( ref_y, 0 )
        ref_y = min ( ref_y, height )

        ref_x = max ( ref_x, 0 )
        ref_x = min ( ref_x, width )

        temp_x = array[:fsr, ref_y, x]
        temp_y = array[:fsr, y, ref_x]

            temp_x = numpy.argmax(temp_x, axis=0)
            temp_y = numpy.argmax(temp_y, axis=0)

            px = scipy.polyfit(x, temp_x, 2)
            py = scipy.polyfit(y, temp_y, 2)

            ref_x = round(- px[1] / (2.0 * px[0]))
            ref_y = round(- py[1] / (2.0 * py[0]))

            if self.show:
                pyplot.title("Finding center of the rings")
                pyplot.cla()
                pyplot.plot(x, temp_x, 'b.', alpha=0.25)
                pyplot.plot(x, scipy.polyval(px, x), 'b-', lw=2)
                pyplot.plot(y, temp_y, 'r.', alpha=0.25)
                pyplot.plot(y, scipy.polyval(py, y), 'r-', lw=2)
                pyplot.gca().yaxis.set_ticklabels([])
                pyplot.axvline(ref_x, ls='--', c='blue', label='x')
                pyplot.axvline(ref_y, ls='--', c='red', label='y')
                pyplot.legend(loc='best')
                pyplot.grid()
                pyplot.ylabel("Iteration number %d" %(i+1))

            # Selecting valid data
            error_x = numpy.abs(temp_x - scipy.polyval(px, x))
            error_y = numpy.abs(temp_y - scipy.polyval(py, y))

            cond_x = numpy.where(error_x <= 3 * error_x.std(), True, False)
            cond_y = numpy.where(error_y <= 3 * error_y.std(), True, False)

            x = x[cond_x]
            y = y[cond_y]

            # Choosing when to stop
            if (abs(old_ref_x - ref_x) <= 2) and (abs(old_ref_y - ref_y) <= 2):

                try:
                    # If the cube was binned this will be useful
                    ref_x = (ref_x - self.header['CRPIX1'] + 1) \
                            * self.header['CDELT1'] + self.header['CRVAL1']

                    # If the cube was binned this will be useful
                    ref_y = (ref_y - self.header['CRPIX2']) \
                            * self.header['CDELT2'] + self.header['CRVAL2']
                except KeyError:
                    pass

                if self.verbose:
                    print(" Rings center found at: [%d, %d]" % (ref_x, ref_y))
                    print(" Done in %.2f s" % (time.time() - now))

                if self.show:
                    pyplot.show()

                return ref_x, ref_y

            else:
                old_ref_x = ref_x
                old_ref_y = ref_y

        if self.show:
            pyplot.show()

        if self.verbose:
            print(" Rings center NOT found.")

        ref_x = self.header['NAXIS1'] // 2
        ref_y = self.header['NAXIS2'] // 2

        # If the cube was binned this will be useful
        try:
            ref_x = (ref_x - self.header['CRPIX1']) \
                    * self.header['CDELT1'] + self.header['CRVAL1']
            ref_y = (ref_y - self.header['CRPIX2']) \
                    * self.header['CDELT2'] + self.header['CRVAL2']
        except:
            pass

        if self.verbose:
            print(" Done in %.2f s" % (time.time() - now))
            print(" Using [%d, %d]." % (ref_x, ref_y))
        return ref_x, ref_y
