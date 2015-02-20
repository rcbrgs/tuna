import numpy
from .file_reader import file_reader
import astropy.io.fits as astrofits
import warnings

class fits ( file_reader ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, file_name = None, log = print, array = None, metadata = [ ] ):
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
            metadata = [ ]
            for key in hdu_list[0].header.keys ( ):
                metadata_dict = { }
                metadata_dict['key'] = key
                metadata_dict['value'] = hdu_list[0].header[key]
                metadata_dict['comment'] = hdu_list[0].header.comments[key]
                self.__metadata.append ( metadata_dict )
            self._is_readable = True
        except OSError as e:
            self.log ( "OSError: %s." % e )
            self._is_readable = False

    def write ( self, file_name = None ):
        if self.__file_name:
            hdu = astrofits.PrimaryHDU ( self.__array )
            if self.__metadata:
                d_columns = { }
                key_list = [ ]
                with warnings.catch_warnings ( ):
                    warnings.simplefilter ( "ignore" )
                    for entry in self.__metadata:
                        comment = entry['comment']
                        value = entry['value']
                        key = entry['key']

                        if len ( key ) > 8:
                            comment += "Original key = " + key + ". "
                            key = key[:7]

                        # check for repeated keys
                        repeat = 1
                        while key in key_list:
                            repeat += 1
                            key = str ( repeat ) + key[: - len ( str ( repeat ) )]

                        key_list.append ( key )

                        if value == None:
                            value = ""
                        elif len ( value ) > 60:
                            comment += "Original value = " + value + ". "
                            value = value [:59]

                        try:
                            hdu.header [key] = ( value, comment )
                        except ValueError as error_message:
                            self.log ( "ValueError: %s." % ( error_message ) )                
                            self.log ( "key = value, len ( value ) + len ( key ): %s = %s, %d" % ( key, value, len ( value ) + len ( key ) ) )
                        
                        # table related stuff
                        if key not in d_columns . keys ( ) :
                            d_columns [ 'key' ] = [ value ]
                        else :
                            d_columns [ 'key' ] . append ( [ value ] )
                fits_columns = [ ]
                for s_key in d_columns . keys ( ):
                    fits_columns . append ( astrofits . Column ( name = s_key, array = d_columns [ s_key ], format = 'A' ) )
                fits_columns_definition = astrofits . ColDefs ( fits_columns )
                # The new_table method will be deprecated, when it is, use the commented line below.
                fits_table_hdu = astrofits . new_table ( fits_columns_definition )                
                #fits_table_hdu = astrofits . BinTableHDU . from_columns ( fits_columns_definition )
                hdu_list = astrofits.HDUList ( [ hdu, fits_table_hdu ] )
                hdu_list.writeto ( "table_" + self.__file_name )

            hdu_list = astrofits.HDUList ( [hdu] )
            hdu_list.writeto ( self.__file_name )
