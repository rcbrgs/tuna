import numpy
from .file_reader import file_reader
import astropy.io.fits as astrofits
import warnings

class fits ( file_reader ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, file_name = None, log = None, image_ndarray = None ):
        super ( fits, self ).__init__ ( )
        if log:
            self.log = log
        else:
            self.log = print

        self._file_name = file_name
        self._image_ndarray = image_ndarray

    def get_image_ndarray ( self ):
        return self._image_ndarray

    def read ( self ):
        if self._file_name == None:
            self.log ( "No file_name for FITS read." )
            self._is_readable = False

        self.log ( "Trying to read file %s as FITS file." % self._file_name )
        try:
            with warnings.catch_warnings ( ):
                warnings.simplefilter ( "ignore" )
                hdu_list = astrofits.open ( self._file_name )
            self.log ( "File %s opened as a FITS file." % self._file_name )
            self._image_ndarray = hdu_list[0].data
            self.log ( "Assigned data section of first HDU as the image ndarray." )
            self._is_readable = True
        except OSError as e:
            self.log ( "OSError: %s." % e )
            self._is_readable = False

    def write ( self, file_name = None ):
        if file_name != None:
            self.__file_name = file_name
        if self.__file_name == None:
            self.log ( "No file_name for FITS write, aborting." )
            return
        
        hdu = astrofits.PrimaryHDU ( self._image_ndarray )
        hdu_list = astrofits.HDUList ( [hdu] )
        hdu_list.writeto ( self.__file_name )
