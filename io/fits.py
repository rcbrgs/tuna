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
                   metadata = { },
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
            self.log ( "debug: No file_name for FITS read." )
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
            metadata = { }
            for key in hdu_list [ 0 ].header.keys ( ):
                metadata_value   = hdu_list [ 0 ].header [ key ]
                metadata_comment = hdu_list [ 0 ].header.comments [ key ]
                self.__metadata [ key ] = ( metadata_value, metadata_comment )
            #self.log ( "debug: metadata = %s" % ( str ( self.__metadata ) )  )
                
            self._is_readable = True
        except OSError as e:
            self.log ( "debug: OSError: %s." % e )
            self._is_readable = False

    def write ( self, file_name = None ):
        if self.__file_name:
            hdu = astrofits.PrimaryHDU ( self.__array )
            if self.__metadata:
                #self.log ( "debug: self.__metadata = %s" % ( str ( self.__metadata ) ) )
                columns = { }
                key_list = [ ]
                with warnings.catch_warnings ( ):
                    warnings.simplefilter ( "ignore" )
                    for key in self.__metadata.keys ( ):
                        #self.log ( "debug: self.__metadata [ %s ] = %s" % ( str ( key ), str ( self.__metadata [ key ] ) ) )
                        comment  = self.__metadata [ key ] [ 1 ]
                        #value    = self.__metadata [ key ] [ 0 ]
                        value = ""
                        for metadata_value in self.__metadata [ key ] [ 0 ]:
                            if ( value == "" ):
                                value += str ( metadata_value )
                            else:
                                value += ", " + str ( metadata_value )

                        if value == None:
                            value = ""

                        max_fits_parameter_value = 6000
                        if len ( value ) > max_fits_parameter_value:
                            comment += ' Original values: ' + value
                            value = value [ : max_fits_parameter_value - 1 ]

                        #fits_key = self.__metadata [ key ] [ 0 ]

                        #self.log ( "debug: comment = %s" % str ( comment ) )
                        #self.log ( "debug: value = %s" % str ( value ) )
                        #self.log ( "debug: fits_key = %s" % str ( fits_key ) )

                        fits_key = key
                        if len ( fits_key ) > 8:
                            comment += " Original key = " + key + ". "
                            fits_key = key[:7]

                        # check for repeated keys
                        repeat = 1
                        while fits_key in key_list:
                            repeat += 1
                            fits_key = str ( repeat ) + fits_key [ : - len ( str ( repeat ) ) ]

                        key_list.append ( fits_key )

                        try:
                            hdu.header [ fits_key ] = ( value, comment )
                        except ValueError as error_message:
                            self.log ( "error: ValueError: %s." % ( error_message ) )                
                            self.log ( "error: fits_key = %s, len ( value ) = %d" % ( fits_key, len ( value ) ) )
                        
            hdu_list = astrofits.HDUList ( [ hdu ] )
            hdu_list.writeto ( self.__file_name )

    def write_metadata_table ( self ):
        if not self.__metadata:
            return

        columns = { }
        for key in self.__metadata.keys ( ):
            values = self.__metadata [ key ] [ 0 ]
            distinct_values = set ( values )
            if ( len ( distinct_values ) > 2 ):
                #self.log ( "debug: more than 2 distinct values: %s." % str ( distinct_values ) )
                format_string = "A21"
                columns [ key ] = ( values, format_string )
        #self.log ( "debug: columns.keys ( ) = %s" % str ( columns.keys ( ) ) )

        fits_columns = [ ]
        for key in columns.keys ( ):
            #self.log ( "debug: appending column %s with array %s and format %s." % ( key, 
            #                                                                         columns [ key ] [ 0 ], 
            #                                                                         columns [ key ] [ 1 ] ) )
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
