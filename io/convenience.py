import logging

from .can import can
from .fits import fits

def read ( file_name ):
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
    __version__ = '0.1.1'
    changelog = {
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
