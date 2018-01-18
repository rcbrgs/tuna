"""This module's scope is the method of finding the image center exploiting its
symmetry. Therefore its applicability is limited to highly symmetric images.

Example::

    >>> import tuna
    >>> barycenter = tuna.io.read("tuna/test/unit/unit_io/" \
                                  "G094_03_wrapped_phase_map.fits" )
    >>> tuna.tools.phase_map.find_image_center_by_symmetry(
            data = barycenter.array)
    (219, 256)
"""
__version__ = "0.1.1"
__changelog = {
    "0.1.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.0": {"Tuna": "0.14.0", "Change": "improved documentation."}
}

import logging
import numpy
import time

class ImageCenterBySymmetry(object):
    """This class responsibility is to find the center of an image by finding the
    row and the column that split the image with the highest degree of symmetry.
    
    If a cube is received, it will use the first plane as its input.

    Its constructor signature is:

    Parameters:

    * array : numpy.ndarray
        Containing the image whose center we intend to find.
    """
    def __init__(self, array = numpy.ndarray):
        super(self.__class__, self).__init__()
        
        self.log = logging.getLogger(__name__)

        self.__input_array = None
        if array.ndim == 2:
            self.__input_array = array
        elif array.ndim == 3:
            self.__input_array = array[0, :, :]
        else:
            self.log("Incorrect ndims for input array.")
        self.__center_row = None
        self.__center_col = None

    def get_center(self):
        """Access the center coordinates. Will trigger a find if the center is
        yet unknown.

        Returns:

        * unnamed variable : tuple of 2 integers
            Containing the column and row indexes for the center.
        """
        if ((self.__center_row is not None) and
            (self.__center_col is not None)):
            return (self.__center_row, self.__center_col)
        else:
            self.find_center()
            return(self.__center_row, self.__center_col)

    def find_center(self):
        """This method's goal is to find the center of the image, by splitting
        the image into same-sized chunks, where the relative distances to the
        center are the same. The center will have circular symmetry, and
        therefore these chunks will be very similar.
        """

        input = self.__input_array
        
        self.log.debug("Searching for most symmetric by-row split.")
        row_results = numpy.ndarray(shape = (input.shape[0]))
        row_results.fill(numpy.inf)
        sixteenth = int(input.shape[0] / 16)
        for row in range(sixteenth, sixteenth * 15):
            bottom = input[row - sixteenth : row - 1, :]
            top = input[row + 1 : row + sixteenth, :]
            top = top[: : -1, :]
            difference = bottom - top
            row_results[row] = numpy.sum(numpy.abs(difference))
        self.log.debug(row_results)
        self.__center_row = numpy.argmin(row_results)

        self.log.debug("Searching for most symmetric columnar split.")
        col_results = numpy.ndarray(shape = (input.shape[1]))
        col_results.fill(numpy.inf)
        sixteenth = int(input.shape[1] / 16)
        for col in range(sixteenth, sixteenth * 15):
            left = input[:, col - sixteenth : col - 1]
            right = input[:, col + 1 : col + sixteenth]
            right = right[:, : : -1]
            difference = left - right
            col_results[col] = numpy.sum(numpy.abs(difference))
        self.log.debug(col_results)
        self.__center_col = numpy.argmin(col_results)

        self.log.debug("Center near ( %d, %d )." % (
            self.__center_row, self.__center_col))
        
def find_image_center_by_symmetry(data = numpy.ndarray):
    """Conveniently wrap the search for the center of the input image.

    Parameters:

    * data : numpy.ndarray
        Should receive the data where a highly symmetric image can be found.

    Returns:

    * iit_center : tuple of 2 integers
        Containing the column and row of the found center.
    """
    start = time.time()

    log = logging.getLogger(__name__)

    o_finder = ImageCenterBySymmetry(array = data)
    iit_center = o_finder.get_center()
    log.debug("iit_center = %s" % str(iit_center))

    log.debug("find_image_center_by_symmetry() took %ds." % (
        time.time() - start))
    return iit_center
