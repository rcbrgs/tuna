"""
The scope of this module is to find rings within 2D FP spectrographs.
"""

import logging
import math
import numpy
import tuna

class rings_2d_finder ( object ):
    """
    The responsibility of this class is to find all rings contained in a bidimensional numpy array provided by the user. It should return ndarrays containing the pixels, and lists of the rings centers and radii.
    """

    def __init__ ( self, array ):
        self.log = logging.getLogger ( __name__ )
        self.__version__ = '0.1.2'
        self.changelog = {
            '0.1.2' : "Moved percentile on threshold to 10% to 'get' more rings.",
            '0.1.1' : "Changed threshold for begin a filling region from 10% to 1% of image pixels, to account for images with many pixels.",
            '0.1.0' : "Initial version." }

        self.array = array
        self.result = { 'radii'   : [ ],
                        'ndarray' : { } }
        
    def execute ( self ):
        """
        Attempt to find a ring by:
        - get the map of the largest finite difference for each point and its neighbours. The idea being that for circular symmetry, such as found on FP spectrographs, pixels on the same "ring" should have similar intensities ( and therefore small finite differences when they are neighbours), while pixels from the "next" or "previous" ring should have different intensities, and therefore relatively greater finite differences.
        - segment the image according to a threshold on the differences (ring borders should have large differences). This results in an image with the rings, and a "ridge" precisely where the finite difference changes signal along the direction.
        
        - find a center. 
        - calculate the distances to center.
        - populate and dispatch the result.
        """

        cols = self.array.shape [ 0 ]
        rows = self.array.shape [ 1 ]

        max_differences = numpy.zeros ( shape = self.array.shape )
        
        nw_finite_differences = numpy.zeros ( shape = self.array.shape )
        nn_finite_differences = numpy.zeros ( shape = self.array.shape )
        ne_finite_differences = numpy.zeros ( shape = self.array.shape )
        ww_finite_differences = numpy.zeros ( shape = self.array.shape )

        ee_finite_differences = numpy.zeros ( shape = self.array.shape )
        sw_finite_differences = numpy.zeros ( shape = self.array.shape )
        ss_finite_differences = numpy.zeros ( shape = self.array.shape )
        se_finite_differences = numpy.zeros ( shape = self.array.shape )

        """
        To simplify finite difference map generation, a 1-pixel border will be ignored.
        """
        for col in range ( 1, cols - 1 ):
            for row in range ( 1, rows - 1 ):
                nw_difference = self.array [ col ] [ row ] - self.array [ col - 1 ] [ row - 1 ]
                nn_difference = self.array [ col ] [ row ] - self.array [ col     ] [ row - 1 ]
                ne_difference = self.array [ col ] [ row ] - self.array [ col + 1 ] [ row - 1 ]
                ww_difference = self.array [ col ] [ row ] - self.array [ col - 1 ] [ row     ]
                
                ee_difference = self.array [ col ] [ row ] - self.array [ col + 1 ] [ row     ]
                sw_difference = self.array [ col ] [ row ] - self.array [ col - 1 ] [ row + 1 ]
                ss_difference = self.array [ col ] [ row ] - self.array [ col     ] [ row + 1 ]
                se_difference = self.array [ col ] [ row ] - self.array [ col + 1 ] [ row + 1 ]
                
                max_difference = max ( abs ( nw_difference ),
                                       abs ( nn_difference ),
                                       abs ( ne_difference ),
                                       abs ( ww_difference ),
                                       abs ( ee_difference ),
                                       abs ( sw_difference ),
                                       abs ( ss_difference ),
                                       abs ( se_difference ) )

                if max_difference == nw_difference:
                    nw_finite_differences [ col ] [ row ] = 1
                if max_difference == nn_difference:
                    nn_finite_differences [ col ] [ row ] = 1
                if max_difference == ne_difference:
                    ne_finite_differences [ col ] [ row ] = 1
                else:
                    ne_finite_differences [ col ] [ row ] = -1
                if max_difference == ww_difference:
                    ww_finite_differences [ col ] [ row ] = 1
                
                if max_difference == ee_difference:
                    ee_finite_differences [ col ] [ row ] = 1
                if max_difference == sw_difference:
                    sw_finite_differences [ col ] [ row ] = 1
                if max_difference == ss_difference:
                    ss_finite_differences [ col ] [ row ] = 1
                if max_difference == se_difference:
                    se_finite_differences [ col ] [ row ] = 1
                
                max_differences [ col ] [ row ] = max_difference

                                                           
        """
        Threshold will be applied at some high percentile. Must make the result image have zeros between the rings. Unfortunately will also zero a "ridge" in the middle of each ring.
        """
        percentile = numpy.percentile ( max_differences, 50 )

        threshold = numpy.where ( max_differences > percentile,
                                  max_differences,
                                  numpy.zeros ( shape = self.array.shape ) )


        """
        To get rid of the ridge, we find all "connected regions", that is, all regions that have the same value in each pixel. Since we thresholded before, each "inter"-rings region should have many pixels, while the rings a much lower value. So we again threshold, on that.
        """
        fill = numpy.zeros ( shape = self.array.shape )
        filling = 1
        
        for col in range ( cols ):
            for row in range ( rows ):
                if fill [ col ] [ row ] == 0:
                    if threshold [ col ] [ row ] != 0:
                        fill [ col ] [ row ] = -1
                        continue
                    to_fill = [ ( col, row ) ]
                    while ( len ( to_fill ) != 0 ):
                        here = to_fill.pop ( )
                        fill [ here [ 0 ] ] [ here [ 1 ] ] = filling
                        for neighbour in tuna.tools.get_pixel_neighbours ( ( here [ 0 ], here [ 1 ] ), threshold ):
                            if fill [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] != 0:
                                continue
                            if threshold [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] != 0:
                                continue
                            to_fill.append ( neighbour )
                    filling += 1

        max_filling = filling
        pixels_total = self.array.shape [ 0 ] * self.array.shape [ 1 ]
        continuous_zero_regions = numpy.zeros ( shape = self.array.shape )
        for filling in range ( 1, max_filling ):
            filling_array = numpy.where ( fill == filling,
                                          numpy.ones ( shape = self.array.shape ),
                                          numpy.zeros ( shape = self.array.shape ) )
            filling_count = numpy.sum ( filling_array )
            if filling_count / pixels_total >= 0.01:
                self.log.info ( "Filling {} has {} pixels.".format ( filling, filling_count ) )
                continuous_zero_regions += filling_array
            else:
                self.log.info ( "Ignoring filling {} since it has {} pixels ({}%)".format (
                    filling, filling_count, filling_count / pixels_total ) )

        """
        Now we have an image with zeros in the "rings" and ones in the "inter"-rings regions.
        This should hold as long as there is at least some part of the image that contains the ring; because the whole approach relies on thresholding against the large difference in intensity for pixels on the ring and outside the ring, for a given spectrograph.

        We now must know how many rings are there. It will be number of disconnected "inter"-rings regions, as long as they are large enough ( to avoid "islands" of zeros inside the rings ).
        """
        connected_regions = [ ]
        considered = numpy.zeros ( shape = self.array.shape )
        max_length = 0
        for col in range ( cols ):
            for row in range ( rows ):
                if considered [ col ] [ row ] != 0:
                    continue
                value = continuous_zero_regions [ col ] [ row ]
                if value != 0:
                    considered [ col ] [ row ] = 1
                    continue
                new_region = tuna.tools.get_connected_region ( ( col, row ),
                                                               continuous_zero_regions, considered )
                connected_regions.append ( new_region )
                self.log.debug ( "new_region with len = {}".format ( len ( new_region ) ) )
                if len ( new_region ) > max_length:
                    max_length = len ( new_region )

        probable_rings = [ ]
        for region in connected_regions:
            if len ( region ) > max_length / 5:
                self.log.info ( "Probable ring region with {} pixels.".format ( len ( region ) ) )
                probable_rings.append ( region )

        """
        Now we create one array for each ring, for easier access.
        """
        rings = [ ]
        for probable_ring in probable_rings:
            ring_array = numpy.zeros ( shape = self.array.shape )
            for point in probable_ring:
                ring_array [ point [ 0 ] ] [ point [ 1 ] ] = 1
            rings.append ( ring_array )

        """
        If there are no pixels for a ring that "touch" the borders of the image, that ring is properly contained within the image, and we can know its center.
        """

        probable_centers = [ ]
        for ring in probable_rings:
            broken_ring = False
            average_col = 0
            average_row = 0
            for point in ring:
                if ( point [ 0 ] < 3 or
                     point [ 1 ] < 3 or
                     point [ 0 ] > self.array.shape [ 0 ] -3 or
                     point [ 1 ] > self.array.shape [ 0 ] -3 ):
                    broken_ring = True
                    break
                average_col += point [ 0 ]
                average_row += point [ 1 ]
            average_col /= len ( ring )
            average_row /= len ( ring )
            if broken_ring:
                self.log.info ( "Ignoring broken ring" )
                continue

            """
            Spectrographs with central "blobs" instead of well-defined rings are too sensitive to noise for this algorithm to be reliable; so ignore them.
            """
            max_col = 0
            min_col = self.array.shape [ 1 ]
            max_row = 0
            min_row = self.array.shape [ 1 ]
            for point in ring:
                max_col = max ( point [ 0 ], max_col )
                min_col = min ( point [ 0 ], min_col )
                max_row = max ( point [ 1 ], max_row )
                min_row = min ( point [ 1 ], min_row )
                
            col_diff = max_col - min_col
            row_diff = max_row - min_row
            if ( max_col - min_col < 0.25 * self.array.shape [ 0 ] or
                 max_row - min_row < 0.25 * self.array.shape [ 1 ] ):
                self.log.info ( "Ignoring ring with too small span." )
                continue
            
            probable_centers.append ( ( average_col, average_row ) )
            self.log.info ( "probable center: {}, {}".format ( average_col, average_row ) )

        """
        If we have centers, we can obtain the radii.
        """

        distances = [ ]
        for center in probable_centers:
            for ring in rings:
                average_ring_center_distance = 0
                for col in range ( cols ):
                    for row in range ( rows ):
                        if ring [ col ] [ row ] == 1:
                            average_ring_center_distance += math.sqrt ( ( col - center [ 0 ] ) ** 2 +
                                                                        ( row - center [ 1 ] ) ** 2 )
                average_ring_center_distance /= numpy.sum ( ring )
                distances.append ( average_ring_center_distance )
                        
        
        self.log.info ( "radii = {}".format ( distances ) )
            
        """
        Saving all results for return to user.
        """
            
        self.result = { 'radii'   : distances,
                        'ndarray' : { 'max' : max_differences,
                                      'nw' : nw_finite_differences,
                                      'nn' : nn_finite_differences,
                                      'ne' : ne_finite_differences,
                                      'ww' : ww_finite_differences,
                                      
                                      'ee' : ee_finite_differences,
                                      'sw' : sw_finite_differences,
                                      'ss' : ss_finite_differences,
                                      'se' : se_finite_differences,
                                      'threshold' : threshold,
                                      'fill' : fill,
                                      'continuous' : continuous_zero_regions,
                                      },
                        'rings' : rings,
                        'probable_centers' : probable_centers,
                        }

def find_rings_2d ( array ):
    """
    Attempts to find rings contained in a 2D numpy ndarray input.
    Returns a structure with the following format:
    result = { 'radii'   : [ ],  # list of radii for rings
               'ndarray' : { 'max', # array where each pixel has the value of the max difference between itself and its neighbours, in the original array.
                             'nw', # array where pixels have max difference with regards to their nw neighbour
                             'nn',
                             'ne',
                             'ww',
                             'ee',
                             'sw',
                             'ss',
                             'se',
                             'threshold', # array where inter-rings are 0s and rings are 1s
                             'fill',
                             'continuous'
                            } 
                'rings',
                'probable_centers'
              }
    """

    finder = rings_2d_finder ( array )
    finder.execute ( )
    return finder.result
