import numpy
from .file_reader import file_reader
import astropy.io.fits as astrofits
import warnings

class fits ( file_reader ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, 
                   file_name = None, 
                   log = print, 
                   array = None, 
                   metadata = [ ] ):
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

        self.log ( "debug: Trying to read file %s as FITS file." % self.__file_name )
        try:
            with warnings.catch_warnings ( ):
                warnings.simplefilter ( "ignore" )
                hdu_list = astrofits.open ( self.__file_name )
            self.log ( "info: File %s opened as a FITS file." % self.__file_name )
            self.__array = hdu_list[0].data
            self.log ( "debug: Assigned data section of first HDU as the image ndarray." )
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
                            self.log ( "error: ValueError: %s." % ( error_message ) )                
                            self.log ( "error: key = value, len ( value ) + len ( key ): %s = %s, %d" % ( key, value, len ( value ) + len ( key ) ) )
                        
            hdu_list = astrofits.HDUList ( [hdu] )
            hdu_list.writeto ( self.__file_name )

    def write_metadata_table ( self ):
        if not self.__metadata:
            return

        d_metadata = { }
        with warnings.catch_warnings ( ):
            warnings.simplefilter ( "ignore" )
            for entry in self.__metadata:
                value = entry['value']
                key = entry['key']
                if value != None:
                    d_metadata [ key ] = value
        #self.log ( "d_metadata = %s" % str ( d_metadata ) )

        d_splitted = { }
        for s_key in d_metadata.keys ( ):
            sl_values = d_metadata [ s_key ].split ( "," )
            d_splitted [ s_key ] = sl_values

        d_columns = { }
        for s_key in d_splitted.keys ( ):
            sl_values = d_splitted [ s_key ]
            ss_distinct_values = set ( sl_values )
            if ( len ( ss_distinct_values ) > 2 ):
                s_format = "A21"
                d_columns [ s_key ] = ( sl_values, s_format )
        #self.log ( "d_columns = %s" % str ( d_columns ) )
        #self.log ( "d_columns.keys ( ) = %s" % str ( d_columns.keys ( ) ) )

        fits_columns = [ ]
        for s_key in d_columns.keys ( ):
            #self.log ( "Appending column %s." % s_key )
            fits_columns . append ( astrofits . Column ( name = s_key, 
                                                         array  = d_columns [ s_key ] [ 0 ], 
                                                         format = d_columns [ s_key ] [ 1 ] ) )

        fits_columns_definition = astrofits . ColDefs ( fits_columns )
        # The new_table method will be deprecated, when it is, use the commented line below.
        fits_table_hdu = astrofits . new_table ( fits_columns_definition )                
        #fits_table_hdu = astrofits . BinTableHDU . from_columns ( fits_columns_definition )
        o_primary_hdu = astrofits.PrimaryHDU ( )
        hdu_list = astrofits.HDUList ( [ o_primary_hdu, fits_table_hdu ] )
        hdu_list.writeto ( "table_" + self.__file_name )
