import numpy
from .file_reader import file_reader
import astropy.io.fits as astrofits
import warnings

class fits ( file_reader ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, file_name = None, log = print, array = None, metadata = { } ):
        super ( fits, self ).__init__ ( )
        self.log = log
        self.__file_name = file_name
        self.__array = array
        self.__metadata = metadata

    def get_array ( self ):
        return self.__array

    def get_metadata ( self ):
        return self.__metadata

    def read ( self ):
        if self.__file_name == None:
            self.log ( "No file_name for FITS read." )
            self._is_readable = False

        self.log ( "Trying to read file %s as FITS file." % self.__file_name )
        try:
            with warnings.catch_warnings ( ):
                warnings.simplefilter ( "ignore" )
                hdu_list = astrofits.open ( self.__file_name )
            self.log ( "File %s opened as a FITS file." % self.__file_name )
            self.__array = hdu_list[0].data
            self.log ( "Assigned data section of first HDU as the image ndarray." )
            for key in hdu_list[0].header.keys ( ):
                self.__metadata[key] = hdu_list[0].header[key]
            self._is_readable = True
        except OSError as e:
            self.log ( "OSError: %s." % e )
            self._is_readable = False

    def write ( self, file_name = None ):
        if self.__file_name:
            hdu = astrofits.PrimaryHDU ( self.__array )
            if self.__metadata:
                with warnings.catch_warnings ( ):
                    warnings.simplefilter ( "ignore" )
                    for key in self.__metadata.keys ( ):
                        value = self.__metadata[key]
                        if ( len ( value ) + len ( key ) ) > 68:
                            key = key [:7]
                            value = value [:59]
                        key = key.replace ( "\t", " " )
                        try:
                            hdu.header [key] = value
                        except ValueError as error_message:
                            self.log ( "ValueError: %s." % ( error_message ) )                
                            self.log ( "key = value, len ( value ) + len ( key ): %s = %s, %d" % ( key, value, len ( value ) + len ( key ) ) )
            hdu_list = astrofits.HDUList ( [hdu] )
            hdu_list.writeto ( self.__file_name )
