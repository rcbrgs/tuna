"""
This module's scope covers operations related to the FITS file format.

As much as possible, operations are deferred to astropy.io.fits.
"""

import astropy.io.fits as astrofits
import copy
import logging
import math
import numpy
import sys
from tuna.io.file_reader import file_reader
import tuna
import warnings

class fits ( file_reader ):
    """
    This class' responsibility is to operate on FITS files.

    Its constructors signature is:

    Parameters:

    * array : numpy.ndarray : defaults to None
        Contains the data to be written to a file.
    
    * file_name : string : defaults to None
        Contains the full location of a file to be read, or to be written to.

    * metadata : dictionary : defaults to { }
        Contains metadata to be written as a FITS header, or the metadata read from a FITS header.

    * photons : dictionary : defaults to None
        Contains the table of photon counts and positions. It is either supplied to be saved to a file, or generated from the data on a file.

    Example::

        import tuna
        import numpy

        zeros_array = numpy.zeros ( shape = ( 3, 3, 3 ) )
        zeros_file = tuna.io.fits ( array = zeros_array )
        zeros_file.write ( file_name = "test_file.fits" )
        fits_file = tuna.io.fits ( file_name = "test_file.fits" )
        fits_file.read ( )
        fits_file.get_array ( )
        fits_file.get_metadata ( )
    """

    def __init__ ( self, 
                   array = None, 
                   file_name = None, 
                   metadata = { },
                   photons = None ):
        super ( fits, self ).__init__ ( )
        self.__version__ = "0.1.1"
        self.changelog = {
            "0.1.1" : "Tuna 0.14.0 : improved docstrings.",
            "0.1.0" : "Tuna 0.13.0 : handling None data sections from astrofits.open. Improved documentation"
            }
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.__file_name = file_name
        self.__array = array
        self.__metadata = metadata
        self.__photons = photons

    def get_array ( self ):
        """
        This method's goal is to access the current array in this object.

        Returns:

        * self.__array : numpy.ndarray
            Contains the current data stored in this object's array.
        """
        return self.__array

    def get_metadata ( self ):
        """
        This method's goal is to access the current metadata in this object.

        Returns:

        * self.__metadata : dictionary
            Contains the current metadata stored in this object.
        """        
        return self.__metadata

    def read ( self ):
        """
        This method's goal is to read the file specified in the constructor's file_name as a FITS file.

        It will inspect the FITS header and try to do the "best thing" according to how many image HDU lists it finds; if there is only one list, that will be the data. If there are multiple lists, and these lists can be arranged as a mosaic (i.e., there are a "quadratic" number of images - 4, 9, 25, etc) they will. This is done in a counter-clockwise order, if we assume the 0th row and column is the top left of the image.
        """
        self.log.debug ( tuna.log.function_header ( ) )
        found = False

        if self.__file_name == None:
            self.log.debug ( "No file_name for FITS read." )
            self._is_readable = False

        self.log.debug ( "Trying to read file %s as FITS file." % self.__file_name )
        try:
            with warnings.catch_warnings ( ):
                warnings.simplefilter ( "error" )
                hdu_list = astrofits.open ( self.__file_name )
            self.log.debug ( "File %s opened as a FITS file." % self.__file_name )

            # The file might have many HDU lists. If there are no arrays, then the file is invalid.
            hdu_info = hdu_list.info ( output = False )
            self.log.debug ( "hdu_info = {}".format ( hdu_info ) )
            if len ( hdu_info ) == 1:
                self.__array = hdu_list [ 0 ].data
                found = True
                
            invalid_flag = True
            for entry in hdu_info:
                if entry [ 4 ] != ( ):
                    invalid_flag = False
                    break
            if not found and invalid_flag:
                self.log.error ( "File is invalid: no dimensions found in its HDU list." )
                return

            # If the file has a single array, that is its data.
            possible_arrays = [ ]
            for entry_index in range ( len ( hdu_info ) ):
                if hdu_info [ entry_index ] [ 4 ] != ( ):
                    possible_arrays.append ( entry_index )
            if len ( possible_arrays ) == 1:
                self.__array = hdu_list [ possible_arrays [ 0 ] ].data

            # If the file has several arrays, then possibly a mosaic is its data.
            if not found and len ( possible_arrays ) % 4 == 0:
                mosaic = True
                common_ndims = hdu_info [ possible_arrays [ 0 ] ] [ 4 ]
                for entry_index in possible_arrays:
                    if hdu_info [ entry_index ] [ 4 ] != common_ndims:
                        self.log.info ( "Cannot build a mosaic since HDU lists have different sizes." )
                        mosaic = False
                if mosaic:
                    self.log.debug ( "Creating a mosaic from the multiple HDU lists of the file." )
                    multiplier = math.sqrt ( len ( possible_arrays ) )
                    cols = common_ndims [ 1 ] * multiplier
                    rows = common_ndims [ 0 ] * multiplier
                    self.__array = numpy.zeros ( shape = ( cols, rows ) )
                    cursor_col = 0
                    cursor_row = 0
                    for entry in possible_arrays:
                        self.log.debug ( "Adding HDU list {} to position ( {}, {} ).".format (
                            entry, cursor_col, cursor_row ) )
                        self.log.debug ( "Splicing array {} into {}, {}".format (
                            hdu_list [ entry ].data.shape, cursor_col, cursor_row ) )
                        self.__array [ cursor_col : cursor_col + common_ndims [ 1 ],
                                       cursor_row : cursor_row + common_ndims [ 0 ] ] = hdu_list [ entry ].data
                        cursor_row += common_ndims [ 0 ]
                        if cursor_row >= common_ndims [ 0 ] * multiplier:
                            cursor_row = 0
                            cursor_col += common_ndims [ 1 ]
                
            if type ( self.__array ) == None:
                if len ( possible_arrays ) > 1:
                    self.log.error ( "File has several distinct entries for data, and Tuna doesn't know how to parse it." )
                self.log.error ( "Data section of the file is None!" )
            else:
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
        """
        This method's goal is to write the object's current array and metadata as a FITS file named file_name.

        Parameters:

        * file_name: string
            Contains a valid path for an yet non-existing file.
        """
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
        """
        This method's goal is to write the object's metadata as a FITS table file.

        It will write the file at the path "metadata\_" + self.__file_name.
        """
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
        """
        This method's goal is to write the object's photons dictionary as a FITS table file.

        It will write the file at the path "photons\_" + self.__file_name.
        """
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
