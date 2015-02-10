"""
This model corresponds to the idea that a Fabry-Perot data file should consist of concentric rings of homogeneous values.
This will not be exact because of noise. Therefore, if we are able to fit the model to most of a data file, the parts that do not fit well might be noise.
"""

import math
import numpy
import scipy
import scipy.interpolate as interpolate
from scipy import stats

def get_free_spectral_range ( array = numpy.ndarray ):
    """
    A quick-and-dirty way to measure the free spectral range in number of channels.
    The method subtracts each frame of the data-cube from the
    first one. Therefore, frames similar to the first will
    have values near zero.
    Then, it calculates the absolute value of the differences and 
    accumulates a sum in X and Y. 
    The FSR is where the resulting spectrum is minimum,
    excluding (of course), the first one.

    Originally written by Bruno Quint for phmxtractor, adapted by Renato Borges.
    """

    print ( "Finding the free-spectral-range." )

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

def find_concentric_rings_center_old ( array = numpy.ndarray ):
    """
    Function used to find the center of the rings inside a FP data-cube.
    Originally developed by Bruno Quint, for phmxtractor.py, adapted by Renato Borges for Tuna.
    """

    # Renaming some variables
    width = array.shape[0]
    height = array.shape[1]
    free_spectral_range = get_free_spectral_range ( array = array )
    fsr = round ( free_spectral_range )

    # Choosing the points
    x = ( numpy.linspace ( 0.2, 0.8, 500 ) * width ).astype ( int )
    y = ( numpy.linspace ( 0.2, 0.8, 500 ) * height ).astype ( int )

    ref_x = width / 2
    ref_y = height / 2

    print ( "Start center finding." )
    old_ref_x = ref_x
    old_ref_y = ref_y

    for i in range ( 6 ):
        ref_y = max ( ref_y, 0 )
        ref_y = min ( ref_y, height )

        ref_x = max ( ref_x, 0 )
        ref_x = min ( ref_x, width )

        temp_x = array[:fsr, ref_y, x]
        temp_y = array[:fsr, y, ref_x]

        temp_x = numpy.argmax ( temp_x, axis = 0 )
        temp_y = numpy.argmax ( temp_y, axis = 0 )
        
        px = scipy.polyfit ( x, temp_x, 2 )
        py = scipy.polyfit ( y, temp_y, 2 )
        
        ref_x = round ( - px[1] / ( 2.0 * px[0] ) )
        ref_y = round ( - py[1] / ( 2.0 * py[0] ) )
        
        # Selecting valid data
        error_x = numpy.abs ( temp_x - scipy.polyval ( px, x ) )
        error_y = numpy.abs ( temp_y - scipy.polyval ( py, y ) )
        
        cond_x = numpy.where ( error_x <= 3 * error_x.std ( ), True, False )
        cond_y = numpy.where ( error_y <= 3 * error_y.std ( ), True, False )
        
        x = x[cond_x]
        y = y[cond_y]
        
        # Choosing when to stop
        if ( ( abs ( old_ref_x - ref_x ) <= 2 ) and 
             ( abs ( old_ref_y - ref_y ) <= 2 ) ):
            #try:
            #    # If the cube was binned this will be useful
            #    ref_x = ( ref_x - self.header['CRPIX1'] + 1 ) * self.header['CDELT1'] + self.header['CRVAL1']
            #
            #    # If the cube was binned this will be useful
            #    ref_y = (ref_y - self.header['CRPIX2']) * self.header['CDELT2'] + self.header['CRVAL2']
            #except KeyError:
            #    pass
            print ( "Rings center found at: [%d, %d]" % ( ref_x, ref_y ) )
            return ref_x, ref_y
        else:
            old_ref_x = ref_x
            old_ref_y = ref_y

    print ( "Rings center NOT found." )

    #ref_x = self.header['NAXIS1'] // 2
    #ref_y = self.header['NAXIS2'] // 2
    
    # If the cube was binned this will be useful
    #try:
    #    ref_x = (ref_x - self.header['CRPIX1']) \
        #            * self.header['CDELT1'] + self.header['CRVAL1']
    #    ref_y = (ref_y - self.header['CRPIX2']) \
        #            * self.header['CDELT2'] + self.header['CRVAL2']
    #except:
    #    pass

    return ref_x, ref_y

def find_concentric_rings_center ( ia_array = numpy.ndarray ):
    """
    Function used to find the center of the rings inside a FP data-cube.
    """

    from ..get_pixel_neighbours import get_pixel_neighbours

    # Renaming some variables
    width = ia_array.shape[1]
    height = ia_array.shape[2]
    free_spectral_range = get_free_spectral_range ( array = ia_array )
    fsr = round ( free_spectral_range )

    i_center_row = int ( height / 2 )
    i_center_col = int ( width / 2 )
    #f_distance = min ( i_center_row, i_center_col ) / 2
    f_distance = 10
    i_distance = int ( f_distance )

    print ( "Start center finding." )

    tl_neighbourhood = get_pixel_neighbours ( array = ia_array[0,:,:], position = ( i_center_row, i_center_col ) )
    f_current_max_similitude = get_ring_similitude ( ia_array = ia_array[0,:,:], it_center = ( i_center_row, i_center_col ), f_distance = 5 )
    t_current_max_similitude_pixel = ( i_center_row, i_center_col )
    b_center_has_moved = True

    print ( "t_current_max_similitude_pixel = %s" % str ( t_current_max_similitude_pixel ) )
    print ( "f_current_max_similitude = %f" % f_current_max_similitude )

    i_row_lowest  = max ( [ 0, i_center_row - i_distance ] )
    i_row_highest = min ( [ i_center_row    + i_distance, ia_array.shape[2] ] )
    i_col_lowest  = max ( [ 0, i_center_col - i_distance ] )
    i_col_highest = min ( [ i_center_col    + i_distance, ia_array.shape[1] ] )

    for row in range ( i_row_lowest, i_row_highest ):
        #print ( "Considering row: %d" % row )
        for col in range ( i_col_lowest, i_col_highest ):
            #print ("Considering ( %d, %d )." % ( row, col ) )
            f_ring_similitude = get_ring_similitude ( ia_array = ia_array[0,:,:], it_center = ( row, col ), f_distance = f_distance )
            if ( f_ring_similitude > f_current_max_similitude ):
                f_current_max_similitude = f_ring_similitude
                t_current_max_similitude_pixel = ( row, col )
                print ( "t_current_max_similitude_pixel = %s" % str ( t_current_max_similitude_pixel ) )
                print ( "f_current_max_similitude = %f" % f_current_max_similitude )

    return t_current_max_similitude_pixel

def get_ring_similitude ( ia_array = numpy.ndarray, it_center = ( int, int ), f_distance = float ):
    """
    Returns the similitude of a ring with radius f_distance centered on it_center with thickness 1.
    Similitude is the number of pixels that have modal value.
    """

    i_center_row = it_center[0]
    i_center_col = it_center[1]

    f_squared_distance = f_distance ** 2
    i_distance = int ( f_distance )

    il_range_rows = range ( ia_array.shape[0] )
    il_range_cols = range ( ia_array.shape[1] )

    i_pixel_count = 0
    ia_photons = numpy.zeros ( shape = ( ia_array.shape[0] * ia_array.shape[1] ) )

    for i_row in il_range_rows:
        for i_col in il_range_cols:
            i_row_distance = abs ( i_center_row - i_row )
            i_col_distance = abs ( i_center_col - i_col )
            if ( ( i_row_distance <= i_distance ) and
                 ( i_col_distance <= i_distance ) ):
                f_squared_distance = ( ( i_row - i_center_row ) ** 2 +
                                       ( i_col - i_center_col ) ** 2 )
                if ( ( f_squared_distance <= f_distance + 1 ) and
                     ( f_squared_distance > f_distance - 1 ) ):
                    ia_photons[i_pixel_count] = ia_array[i_row][i_col] 
                    i_pixel_count += 1

    i_mode = stats.mode ( numpy.array ( ia_photons[:i_pixel_count] ), axis = None )
    return i_mode[1][0]
