"""
This module's scope covers operations related to the can file format.

The Tuna can is a image and metadata file format. It consists of a serializable object (instantiated from the tuna.io.can.can class), where convenience methods (such as algebraic procedures on its arrays) are defined.
"""

from .adhoc import adhoc
from .adhoc_ada import ada
from .file_reader import file_reader
from .fits import fits

import logging
import numpy
import sys
import time
import tuna

class can ( file_reader ):
    """
    This class' responsibilities are to create and operate upon Tuna can files.

    It inherits from :ref:`tuna_io_file_reader_label`.

    Its constructor signature is:

    Parameters:

    * array : numpy.ndarray : defaults to None
        The data to be stored in the can.

    * file_name : string : defaults to None
        The name of the file containing the data.

    * interference_order : integer : defaults to None
        The value of the interference order of the observed light on the data.

    * interference_order_wavelength : integer : defaults to None
        The wavelength, in Angstroms, of the observed light on the data.

    * photons : dictionary : defaults to None
        A dictionary containing the description of each photon count on the data.


    The Tuna can is the preferred internal format for Tuna. Therefore, when most modules are used, they return their result in a can.

    Example usage::

        import tuna
        raw = tuna.io.read ( file_name = "tuna/tuna/test/unit/unit_io/adhoc.ad3" )
        type ( raw )
        Out[3]: tuna.io.can.can
        raw2 = raw + raw
        raw_copy = raw2 - raw
        raw.flipud ( )
        raw.fliplr ( )
        raw.convert_ndarray_into_table ( )
        raw.update ( )
    """
    def __init__ ( self,
                   array = None,
                   file_name = None,
                   interference_order = None,
                   interference_reference_wavelength = None,
                   photons = None ):
        super ( can, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        self.__version__ = "0.1.5"
        self.changelog = {
            "0.1.5" : "Tuna 0.14.0 : improved docstrings.",
            "0.1.4" : "Updated docstring to new documentation style.",
            "0.1.3" : "Docstrings added.",
            "0.1.2" : "Do not update db if that is going to update a file_name to None.",
            "0.1.1" : "Feed info into db upon update, added file_type property.",
            "0.1.0" : "Initial changelogged version."
            }

        self.array = array
        self.file_name = file_name
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.photons = photons

        self.digest = None
        self.file_type = None
        self.ndim = None
        self.shape = None
        self.planes = None
        self.rows = None
        self.cols = None
        self.metadata = None
        self.update ( )

    def __add__ ( self, summand ):
        self.log.debug ( tuna.log.function_header ( ) )

        sum_array = self.array + summand.array
        result = can ( array = sum_array )
        return result

    def __sub__ ( self, subtrahend ):
        self.log.debug ( tuna.log.function_header ( ) )

        subtraction_array = self.array - subtrahend.array
        result = can ( array = subtraction_array )
        return result

    def convert_ndarray_into_table ( self ):
        """
        This method's goal is to convert a numpy.ndarray into a photon table, where the value contained in the array, for each voxel, is considered as a photon count.

        The result is saved in self.photons, which has the following structure (example)::

            self.photons = [
                { 'channel' : 10,
                  'row'     : 128,
                  'col'     : 1,
                  'photons' : 1024 },
                { 'channel' : 11,
                  'row'     : 128,
                  'col'     : 1,
                  'photons' : 700 },
                ...
                { 'channel' : 30,
                  'row'     : 128,
                  'col'     : 128,
                  'photons' : 0 } ]

        """
        self.log.debug ( tuna.log.function_header ( ) )

        start = time.time ( )

        photons = [ ]
        self.log.debug ( "Parsing image into photon table 0% done." )
        last_percentage_logged = 0
        for plane in range ( self.planes ):
            percentage = 10 * int ( plane / self.planes * 10 )
            if percentage > last_percentage_logged:
                self.log.debug ( "Parsing image into photon table %d%% done." % ( percentage ) )
                last_percentage_logged = percentage
            for row in range ( self.rows ):
                for col in range ( self.cols ):
                    photon = { }
                    photon [ 'channel' ] = plane + 1
                    photon [ 'row'     ] = row
                    photon [ 'col'     ] = col
                    if self.ndim == 3:
                        photon [ 'photons' ] = self.array [ plane ] [ row ] [ col ]
                    elif self.ndim == 2:
                        photon [ 'photons' ] = self.array [ row ] [ col ]
                    photons.append ( photon )
        self.log.debug ( "info: parsing image into photon table 100% done." )

        self.photons = photons
        self.log.debug ( "debug: convert_ndarray_into_table() took %ds." % ( time.time ( ) - start ) )

    def convert_table_into_ndarray ( self ):
        """
        This method's goal is to accumulate values from a table (required to be in the same structure as specified in the method convert_ndarray_into_table) into a numpy array.

        It will create an array with the minimal dimensions necessary to hold all photons; therefore if you have "photonless" regions in a data cube, and convert it to a table, then back into a cube, you might end with a numpy.ndarray with a different shape than you started.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        planes = 0
        rows = 0
        cols = 0
        for photon in self.photon:
            planes = max ( planes, photon [ 'channel' ] + 1 )
            rows   = max ( rows,   photon [ 'row'     ] )
            cols   = max ( cols,   photon [ 'col'     ] )
        self.ndim = 3
        self.planes = planes
        self.rows = rows
        self.cols = cols
        self.shape = ( planes, rows, cols )

        array = numpy.zeros ( shape = self.shape )

        for photon in self.photons:
            array [ photon [ 'channel ' ] - 1 ] [ photon [ 'row' ] ] [ photon [ 'col' ] ] = photon [ 'photons' ]

        self.array = array

    def _database_refresh ( self ):
        """
        Supposing both the can and the db connection are fine, check if there is an entry on db about this can's array, and create / update it as appropriate.
        """
        if not self.digest:
            self.digest = tuna.tools.get_hash_from_array ( self.array )
        records, sql_success = tuna.db.select_record ( 'datasets', { 'hash' : self.digest } )
        if not sql_success:
            self.log.debug ( "At database_refresh sql_success == False." )
            return
        record = None
        if records:
            record = records [ 0 ]

        function = tuna.db.insert_record
        file_name = self.file_name
        file_type = self.file_type
        if record:
            self.log.debug ( "Can is already on db." )
            function = tuna.db.update_record
            if ( record [ 'file_name' ] != "None" and
                 self.file_name == None ):
                file_name = record [ 'file_name' ]
                file_type = record [ 'file_type' ]
        function ( 'datasets', { 'hash'      : self.digest,
                                 'file_name' : file_name,
                                 'file_type' : file_type } )

    def fliplr ( self ):
        """
        This method's goal is to wrap around numpy.fliplr, which flips a 2D array from left to right (the rightmost column becomes the leftmost one). This is applied to each plane of a cube, or the single plane of a planar image.
        """
        result = numpy.ndarray ( shape = self.array.shape )
        for plane in range ( self.array.shape [ 0 ] ):
            result [ plane ] = numpy.fliplr ( self.array [ plane ] )
        self.array = result

    def flipud ( self ):
        """
        This method's goal is to wrap around numpy.flipud, which flips a 2D array from up to down (the last line becomes the first). This is applied to each plane of a cube, or the single plane of a planar image.
        """
        result = numpy.ndarray ( shape = self.array.shape )
        for plane in range ( self.array.shape [ 0 ] ):
            result [ plane ] = numpy.flipud ( self.array [ plane ] )
        self.array = result

    def info ( self ):
        """
        This method's goal is to output to the current logging.info handler some metadata about the current can.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        self.log.info ( "file_name = %s" % self.file_name )
        self.log.info ( "shape = %s" % str ( self.shape ) )
        self.log.info ( "file_type = %s" % str ( self.file_type ) ) #new add by Julien Penguen 28/07/2017
        self.log.info ( "ndim = %d" % self.ndim )
        self.log.info ( "planes = %d" % self.planes )
        self.log.info ( "rows = %d" % self.rows )
        self.log.info ( "cols = %d" % self.cols )
        self.log.info ( "interference_order = %s" % str ( self.interference_order ) )
        self.log.info ( "interference_reference_wavelength = %s" % str ( self.interference_reference_wavelength ) )

    def read ( self ):
        """
        This method's goal is to read a file content's into a can.
        Will sequentially attempt to read the file as an .ADT, .fits, .AD2 and .AD3 formatted file. The first attempt to succeed is used.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        self.log.debug ( "line %d, before attempting to read file, %s" % ( tuna.log.line_number ( ),
                                                                           tuna.io.system.status ( ) ) )

        if self.file_name:
            if ( self.file_name.startswith ( ".ADT", -4 ) or
                 self.file_name.startswith ( ".adt", -4 ) ):
                ada_object = ada ( file_name = self.file_name )
                ada_object.read ( )
                self.array = ada_object.get_array ( )
                self.metadata = ada_object.get_metadata ( )
                self.__d_photons = ada_object.get_photons ( )
                self.file_type = "adt"
                self.update ( )

            elif ( self.file_name.startswith ( ".fits", -5 ) or
                   self.file_name.startswith ( ".FITS", -5 ) ):
                fits_object = fits ( file_name = self.file_name )
                fits_object.read ( )
                self.array = fits_object.get_array ( )
                self.metadata = fits_object.get_metadata ( )
                self.file_type = "fits"
                self.update ( )

            elif ( self.file_name.startswith ( ".ad2", -4 ) or
                   self.file_name.startswith ( ".AD2", -4 ) or
                   self.file_name.startswith ( ".ad3", -4 ) or
                   self.file_name.startswith ( ".AD3", -4 ) ):
                adhoc_object = adhoc ( file_name = self.file_name )
                adhoc_object.read ( )
                self.array = adhoc_object.get_array ( )
                #self.metadata = adhoc_object.__trailer
                self.file_type = "ada"
                self.update ( )

        self.log.debug ( "After attempting to read file, " + tuna.io.system.status ( ) )

    def update ( self ):
        """
        This method's goal is to clears current metadata, and regenerate this information based on the current contents of the can's array and photon table.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        if ( ( not isinstance ( self.array, numpy.ndarray ) ) and
             self.photons == None ):
            self.log.debug ( "Empty Tuna can." )
            self.metadata = None
            self.ndim = None
            self.shape = None
            self.planes = None
            self.rows = None
            self.cols = None
            return

        if ( not isinstance ( self.array, numpy.ndarray ) ):
            self.convert_table_into_ndarray ( )
            return

        self.ndim = self.array.ndim
        self.shape = self.array.shape
        self.log.debug ( "can.update: self.array.ndim == %d, self.ndim == %d." % ( self.array.ndim, self.ndim ) )
        if self.ndim == 3:
            self.planes = self.array.shape [ 0 ]
            self.rows   = self.array.shape [ 1 ]
            self.cols   = self.array.shape [ 2 ]
        elif self.ndim == 2:
            self.planes = 1
            self.rows   = self.array.shape [ 0 ]
            self.cols   = self.array.shape [ 1 ]
        if ( self.ndim < 2 or
             self.ndim > 3 ):
            self.log.warning ( "ndarray has either less than 2 or more than 3 dimensions." )

        self._database_refresh ( )

    def help(self):
        """
        """
        method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        return method_list
