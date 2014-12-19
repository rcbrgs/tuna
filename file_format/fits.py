import numpy
from sys import path
path.append ( "/home/nix/sync/tuna/" )
from github.file_format import file_format
import astropy.io.fits

class fits ( file_format.file_format ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, file_name = None ):
        self.__file_name = file_name
        self.__is_readable = False
        super ( fits, self ).__init__ ( )

    def get_image_ndarray ( self ):
        return self.__image_ndarray

    def is_readable ( self ):
        return self.__is_readable

    def read ( self ):
        if self.__file_name == None:
            print ( "No file_name for FITS read." )
            return

        print ( "Trying to read file as FITS file." )
        try:
            hdu_list = astropy.io.fits.open ( self.__file_name )
        except OSError as e:
            print ( "OSError: %s." % e )
            raise e
            return
        print ( "File opened as a FITS file." )
        self.__image_ndarray = hdu_list[0].data
        print ( "Assigned data section of first HDU as the image ndarray." )
        self.__is_readable = True
