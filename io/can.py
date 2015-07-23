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
    def __init__ ( self, 
                   array = None,
                   file_name = None,
                   interference_order = None,
                   interference_reference_wavelength = None,
                   photons = None ):
        super ( can, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        self.__version__ = '0.1.1'
        self.changelog = {
            '0.1.1' : "Feed info into db upon update, added file_type property.",
            '0.1.0' : "Initial changelogged version."
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
        result = can ( log = self.log,
                       array = sum_array )
        return result

    def __sub__ ( self, subtrahend ):
        self.log.debug ( tuna.log.function_header ( ) )

        subtraction_array = self.array - subtrahend.array
        result = can ( log = self.log,
                       array = subtraction_array )
        return result

    def convert_ndarray_into_table ( self ):
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

    def database_refresh ( self ):
        """
        Supposing both the can and the db connection are fine, check if there is an entry on db about this can's array, and create / update it as appropriate.
        """
        if not self.digest:
            self.digest = tuna.tools.get_hash_from_array ( self.array )
        record = tuna.db.select_record ( 'datasets', { 'hash' : self.digest } )
        function = tuna.db.insert_record
        if record:
            self.log.info ( "Can is already on db." )
            function = tuna.db.update_record
        function ( 'datasets', { 'hash'      : self.digest,
                                 'file_name' : self.file_name,
                                 'file_type' : self.file_type } )

    def fliplr ( self ):
        result = numpy.ndarray ( shape = self.array.shape )
        for plane in range ( self.array.shape [ 0 ] ):
            result [ plane ] = numpy.fliplr ( self.array [ plane ] )
        self.array = result

    def flipud ( self ):
        result = numpy.ndarray ( shape = self.array.shape )
        for plane in range ( self.array.shape [ 0 ] ):
            result [ plane ] = numpy.flipud ( self.array [ plane ] )
        self.array = result

    def info ( self ):
        self.log.debug ( tuna.log.function_header ( ) )

        self.log.info ( "file_name = %s" % self.file_name )
        self.log.info ( "shape = %s" % str ( self.shape ) )
        self.log.info ( "ndim = %d" % self.ndim )
        self.log.info ( "planes = %d" % self.planes )
        self.log.info ( "rows = %d" % self.rows )
        self.log.info ( "cols = %d" % self.cols )
        self.log.info ( "interference_order = %s" % str ( self.interference_order ) )
        self.log.info ( "interference_reference_wavelength = %s" % str ( self.interference_reference_wavelength ) )

    def read ( self ):
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

        self.database_refresh ( )
