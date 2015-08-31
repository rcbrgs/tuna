import logging

from .can import can
from .fits import fits

def read ( file_name ):
    """
    Will create a tuna can, and attempt to read the specified file_name using the can.read method.

    Returns a tuna can.
    """
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
    Attempts to write a file using the specified input:

    - array: a numpy.ndarray,
    - file_format: a string specifying one of Tuna's known write formats (only "fits" is implemented so far),
    - file_name: a string containing the destiny file path and name.
    - metadata: a structure containing the metadata to be saved as fits headers.
    - photons: a structure containing photon descriptions, in the same format as specified in tuna.io.can.convert_ndarray_into_table.    
    """
    __version__ = '0.1.2'
    changelog = {
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
