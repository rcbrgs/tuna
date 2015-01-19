from .can import can
from file_format.fits import fits

def read ( file_name = None ):
    if file_name:
        tuna_can = can ( file_name = file_name )
        tuna_can.read ( )
        return tuna_can

def write ( file_name = None, array = None, metadata = None, file_format = None ):
    if ( file_format == 'fits' or
         file_format == 'FITS' ):
        fits_io_object = fits ( file_name = file_name, array = array, metadata = metadata )
        fits_io_object.write ( )
