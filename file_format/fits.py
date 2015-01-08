import numpy
from .file_reader import file_reader
import astropy.io.fits
import warnings

class fits ( file_reader ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, file_name = None, log = None ):
        self._file_name = file_name
        if log:
            self.log = log
        else:
            self.log = print
        super ( fits, self ).__init__ ( )

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
                hdu_list = astropy.io.fits.open ( self._file_name )
            self.log ( "File %s opened as a FITS file." % self._file_name )
            self._image_ndarray = hdu_list[0].data
            self.log ( "Assigned data section of first HDU as the image ndarray." )
            self._is_readable = True
        except OSError as e:
            self.log ( "OSError: %s." % e )
            self._is_readable = False
