import astropy.io.fits as astrofits
import copy
import logging
import numpy
import sys
from tuna.io.file_reader import file_reader
import tuna
import warnings

class fits ( file_reader ):
    """
    Class for reading FITS files.

    Consists mostly of a wrapper around Astropy's io.fits module.
    """

    def __init__ ( self, 
                   array = None, 
                   file_name = None, 
                   metadata = { },
                   photons = None ):
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        super ( fits, self ).__init__ ( )

        self.__file_name = file_name
        self.__array = array
        self.__metadata = metadata
        self.__photons = photons

    def get_array ( self ):
        return self.__array

    def get_metadata ( self ):
        return self.__metadata

    def read ( self ):
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__file_name == None:
            self.log.debug ( "No file_name for FITS read." )
            self._is_readable = False

        self.log.debug ( "Trying to read file %s as FITS file." % self.__file_name )
        try:
            with warnings.catch_warnings ( ):
                warnings.simplefilter ( "ignore" )
                hdu_list = astrofits.open ( self.__file_name )
            self.log.info ( "File %s opened as a FITS file." % self.__file_name )
            self.__array = hdu_list[0].data
            self.log.debug ( "Assigned data section of first HDU as the image ndarray." )
            self.log.debug ( "self.__array.ndim == %d" % self.__array.ndim )
            metadata = { }
            for key in hdu_list [ 0 ].header.keys ( ):
                metadata_value   = hdu_list [ 0 ].header [ key ]
                metadata_comment = hdu_list [ 0 ].header.comments [ key ]
                self.__metadata [ key ] = ( metadata_value, metadata_comment )
                
            self._is_readable = True
        except OSError as e:
            self.log.error ( "OSError: %s." % e )
            self._is_readable = False

    def write ( self, file_name = None ):
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__file_name:
            header = astrofits.Header ( )
            if self.__metadata:
                columns = { }
                key_list = [ ]
                for key in self.__metadata.keys ( ):
                    comment  = self.__metadata [ key ] [ 1 ]
                    value = ""
                    for metadata_value in self.__metadata [ key ] [ 0 ]:
                        if ( value == "" ):
                            value += str ( metadata_value )
                        else:
                            value += ", " + str ( metadata_value )

                    if len ( key ) > 8:
                        fits_key = key [ : 8 ]
                        comment += "original key = " + key
                    else:
                        fits_key = key

                    fits_key = fits_key.replace ( ' ', '_' )
                    
                    self.log.debug ( "fits_key = %s" % fits_key )
                    self.log.debug ( "len ( value ) = %d" % len ( value ) )
                    self.log.debug ( "len ( comment ) = %d" % len ( comment ) )

                    card = astrofits.Card ( fits_key, value, comment )
                    self.log.debug ( "str ( card ) = %s" % str ( card ) )
                    header.append ( card )

            hdu = astrofits.PrimaryHDU ( self.__array, header )
            hdu_list = astrofits.HDUList ( [ hdu ] )
            try:
                hdu_list.writeto ( self.__file_name )
            except OSError as e:
                if e == "File '" + self.__file_name + "' already exists.":
                    self.log.error ( "File %s already exists." % self.__file_name )
                    sys.exit ( 1 )

    def write_metadata_table ( self ):
        self.log.debug ( tuna.log.function_header ( ) )

        if not self.__metadata:
            return

        columns = { }
        for key in self.__metadata.keys ( ):
            values = self.__metadata [ key ] [ 0 ]
            distinct_values = set ( values )
            if ( len ( distinct_values ) > 2 ):
                self.log.debug ( "More than 2 distinct values: %s." % str ( distinct_values ) )
                format_string = "A21"
                columns [ key ] = ( values, format_string )

        fits_columns = [ ]
        for key in columns.keys ( ):
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
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__photons == None:
            return

        columns = { }
        columns [ 'channel' ] = [ [ ], "I2" ]
        columns [ 'x' ]       = [ [ ], "I3" ]
        columns [ 'y' ]       = [ [ ], "I3" ]
        columns [ 'photons' ] = [ [ ], "I5" ]

        for entry in self.__photons:
            columns [ 'channel' ] [ 0 ] .append ( self.__photons [ entry ] [ 'channel' ] )
            columns [ 'x' ]       [ 0 ] .append ( self.__photons [ entry ] [ 'x'       ] )
            columns [ 'y' ]       [ 0 ] .append ( self.__photons [ entry ] [ 'y'       ] )
            columns [ 'photons' ] [ 0 ] .append ( self.__photons [ entry ] [ 'photons' ] )

        
        fits_columns = [ ]
        for key in columns.keys ( ):
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
