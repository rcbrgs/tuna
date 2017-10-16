"""
This module's scope covers tools that make data access more convenient.
"""

import logging

from .can import can
from .fits import fits
from .adhoc import adhoc #new add by Julien Penguen 28/07/2017
from .adhoc_ada import ada #new add by Julien Penguen 28/07/2017

def read ( file_name ):
    """
    This function's goal is to create a tuna can, and attempt to read the specified file_name using the can.read ( ) method.

    Parameters:

    * file_name : string
        Specifies an existing file, containing data in a format Tuna understands.

    Returns:

    * tuna_can : tuna.io.can
        Containing the data read from the input file.

    Example::

        import tuna
        tuna.io.read ( "data_file.fits" )
    """
    __version__ = "0.1.0"
    changelog = {
        "0.1.0" : "Tuna 0.13.0 : Added example to docstring."
        }
    log = logging.getLogger ( __name__ )
    log.setLevel ( logging.INFO )
    log.debug ( "Creating a tuna can for file name %s." % file_name )

    if file_name:
        tuna_can = can ( file_name = file_name )
        tuna_can.read ( )
        return tuna_can

def write ( array       = None,
            file_format = None,
            file_name   = None,
            metadata    = None,
            photons   = None ):
    """
    This method's goal is to write a file using the specified input.

    Parameters:

    * array : numpy.ndarray
        The data to be saved in the file.
    * file_format: string
        Specifies one of Tuna's known write formats (only "fits" is implemented so far).
    * file_name: string
        Must contain a valid file path and name.
    * metadata: dictionary
        A structure containing the metadata to be saved as fits headers.
    * photons: dictionary
        A structure containing photon descriptions, in the same format as specified in tuna.io.can.convert_ndarray_into_table ( ).

    Example::

        import tuna
        import numpy

        zeros_array = numpy.zeros ( shape = ( 2, 3, 3 ) )
        tuna.io.write ( array = zeros_array, file_name = "zeros.fits", file_format = "fits" )
    """
    __version__ = '0.1.3'
    changelog = {
        "0.1.3" : "Tuna 0.13.0 : Added example to docstring.",
        '0.1.2' : "Added docstring.",
        '0.1.1' : "Added error message when file format is unknown."
        }
    log = logging.getLogger ( __name__ )
    log.setLevel ( logging.INFO )

    if ( file_format == 'fits' or
         file_format == 'FITS' ):
        fits_io_object = fits ( file_name = file_name,
                                array = array,
                                metadata = metadata,
                                photons = photons )
        fits_io_object.write ( )
        fits_io_object.write_metadata_table ( )
        fits_io_object.write_photons_table ( )
        log.info ( "FITS file written at %s." % str ( file_name ) )
        return

    log.error ( "No file_format '{}' known.".format ( file_format ) )
