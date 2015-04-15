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
                   array = None, 
                   file_name = None, 
                   log = print, 
                   metadata = [ ],
                   photons = None ):
        super ( fits, self ).__init__ ( )
        self.log = log
        self.__file_name = file_name
        self.__array = array
        self.__metadata = metadata
        self.__photons = photons

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
            self.log ( "debug: self.__array.ndim == %d" % self.__array.ndim )
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
                columns = { }
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

        metadata = { }
        with warnings.catch_warnings ( ):
            warnings.simplefilter ( "ignore" )
            for entry in self.__metadata:
                value = entry['value']
                key = entry['key']
                if value != None:
                    metadata [ key ] = value
        #self.log ( "metadata = %s" % str ( metadata ) )

        splitted = { }
        for key in metadata.keys ( ):
            values = metadata [ key ].split ( "," )
            splitted [ key ] = values

        columns = { }
        for key in splitted.keys ( ):
            values = splitted [ key ]
            distinct_values = set ( values )
            if ( len ( distinct_values ) > 2 ):
                format_string = "A21"
                columns [ key ] = ( values, format_string )
        #self.log ( "columns = %s" % str ( columns ) )
        #self.log ( "columns.keys ( ) = %s" % str ( columns.keys ( ) ) )

        fits_columns = [ ]
        for key in columns.keys ( ):
            #self.log ( "Appending column %s." % key )
            fits_columns . append ( astrofits . Column ( name = key, 
                                                         array  = columns [ key ] [ 0 ], 
                                                         format = columns [ key ] [ 1 ] ) )

        fits_columns_definition = astrofits . ColDefs ( fits_columns )
        # The new_table method will be deprecated, when it is, use the commented line below.
        fits_table_hdu = astrofits . new_table ( fits_columns_definition )                
        #fits_table_hdu = astrofits . BinTableHDU . from_columns ( fits_columns_definition )
        primary_hdu = astrofits.PrimaryHDU ( )
        hdu_list = astrofits.HDUList ( [ primary_hdu, fits_table_hdu ] )
        hdu_list.writeto ( "metadata_" + self.__file_name )

    def write_photons_table ( self ):
        if self.__photons == None:
            return

        columns = { }
        columns [ 'channel' ] = [ [ ], "I2" ]
        columns [ 'x' ]       = [ [ ], "I3" ]
        columns [ 'y' ]       = [ [ ], "I3" ]
        columns [ 'photons' ] = [ [ ], "I5" ]

        for entry in self.__photons:
            #self.log ( "debug: columns = %s" % str ( columns ) )
            #self.log ( "debug: columns [ 'channel' ] = %s" % str ( columns [ 'channel' ] ) )
            #self.log ( "debug: columns [ 'channel' ] [ 0 ] = %s" % str ( columns [ 'channel' ] [ 0 ] ) ) 
            columns [ 'channel' ] [ 0 ] .append ( self.__photons [ entry ] [ 'channel' ] )
            columns [ 'x' ]       [ 0 ] .append ( self.__photons [ entry ] [ 'x'       ] )
            columns [ 'y' ]       [ 0 ] .append ( self.__photons [ entry ] [ 'y'       ] )
            columns [ 'photons' ] [ 0 ] .append ( self.__photons [ entry ] [ 'photons' ] )

        
        fits_columns = [ ]
        for key in columns.keys ( ):
            #self.log ( "Appending column %s." % key )
            fits_columns . append ( astrofits . Column ( name = key, 
                                                         array  = columns [ key ] [ 0 ], 
                                                         format = columns [ key ] [ 1 ] ) )

        fits_columns_definition = astrofits . ColDefs ( fits_columns )
        # The new_table method will be deprecated, when it is, use the commented line below.
        fits_table_hdu = astrofits . new_table ( fits_columns_definition )                
        #fits_table_hdu = astrofits . BinTableHDU . from_columns ( fits_columns_definition )
        primary_hdu = astrofits.PrimaryHDU ( )
        hdu_list = astrofits.HDUList ( [ primary_hdu, fits_table_hdu ] )
        hdu_list.writeto ( "photons_" + self.__file_name )
