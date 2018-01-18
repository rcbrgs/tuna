"""This module's scope covers tools that make data access more convenient.
"""
__version__ = "0.1.1"
__changelog = {
    "0.1.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.0": {"Tuna": "0.13.0", "Change": "Added example to docstring."}
}

import logging

from .adhoc import Adhoc
from .adhoc_ada import Ada
from .can import Can
from .fits import Fits

def read(file_name):
    """
    Create a tuna can, and attempt to read the specified file_name using the 
    Can.read ( ) method.

    Parameters:

    * file_name : string
        Specifies an existing file, containing data in a format Tuna 
        understands.

    Returns:

    * tuna_can : tuna.io.can.Can
        Containing the data read from the input file.

    Example::

        import tuna
        tuna.io.read ( "data_file.fits" )
    """
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.debug("Creating a tuna can for file name %s." % file_name)

    if file_name:
        tuna_can = Can(file_name = file_name)
        tuna_can.read()
        return tuna_can

def write (array = None, 
           file_format = None,
           file_name = None, 
           metadata = None,
           photons = None ):
    """Write a file using the specified input.

    Parameters:

    * array : numpy.ndarray
        The data to be saved in the file.
    * file_format: string 
        Specifies one of Tuna's known write formats (only "fits" is implemented 
        so far).
    * file_name: string 
        Must contain a valid file path and name.
    * metadata: dictionary
        A structure containing the metadata to be saved as fits headers.
    * photons: dictionary
        A structure containing photon descriptions, in the same format as 
        specified in tuna.io.can.convert_ndarray_into_table().    

    Example::

        import tuna
        import numpy

        zeros_array = numpy.zeros(shape = (2, 3, 3))
        tuna.io.write(array = zeros_array, file_name = "zeros.fits", 
                       file_format = "fits")
    """
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    if (file_format == 'fits' or
        file_format == 'FITS'):
        fits_io_object = Fits(file_name = file_name, 
                              array = array, 
                              metadata = metadata,
                              photons = photons)
        fits_io_object.write()
        fits_io_object.write_metadata_table()
        fits_io_object.write_photons_table()
        log.info("FITS file written at %s." % str(file_name))
        return

    log.error("No file_format '{}' known.".format(file_format))
