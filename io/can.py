from .adhoc import adhoc
from .adhoc_ada import ada
from tuna.data_cube.cube import cube
from .file_reader import file_reader
from .fits import fits
import numpy
import time
import tuna

class can ( file_reader ):
    def __init__ ( self, 
                   log = print,
                   array = None,
                   cube = None,
                   file_name = None,
                   interference_order = None,
                   interference_reference_wavelength = None,
                   photons = None ):
        super ( can, self ).__init__ ( )
        self.log = log

        self.array = array
        self.cube = cube
        self.file_name = file_name
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.photons = photons

        self.ndim = None
        self.shape = None
        self.planes = None
        self.rows = None
        self.cols = None
        self.metadata = None
        self.update ( )

    def __add__ ( self, summand ):
        result = can ( log = self.log )
        result.cube = self.cube + summand.cube
        result.array = result.cube.get_array ( )

        return result

    def __sub__ ( self, subtrahend ):
        result = can ( log = self.log )
        result.cube = self.cube - subtrahend.cube
        result.array = result.cube.get_array ( )
        
        return result

    def convert_ndarray_into_table ( self ):
        start = time.time ( )

        photons = [ ]
        self.log ( "info: parsing image into photon table 0% done." )
        last_percentage_logged = 0
        for plane in range ( self.planes ):
            percentage = 10 * int ( plane / self.planes * 10 )
            if percentage > last_percentage_logged:
                self.log ( "info: parsing image into photon table %d%% done." % ( percentage ) )
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
        self.log ( "info: parsing image into photon table 100% done." )

        self.photons = photons
        self.log ( "info: convert_ndarray_into_table() took %ds." % ( time.time ( ) - start ) )

    def convert_table_into_ndarray ( self ):
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

    def read ( self ):
        self.log ( "debug: before attempting to read file, " + tuna.io.system.status ( ) )
        if self.file_name:
            if ( self.file_name.startswith ( ".ADT", -4 ) or
                 self.file_name.startswith ( ".adt", -4 ) ):
                ada_object = ada ( file_name = self.file_name,
                                   log = self.log )
                ada_object.read ( )
                self.array = ada_object.get_array ( )
                self.cube = cube ( log = self.log,
                                     data = self.array )
                self.metadata = ada_object.get_metadata ( )
                #self.log ( "debug: self.metadata = %s" % ( str ( self.metadata ) ) )
                self.__d_photons = ada_object.get_photons ( )
            elif ( self.file_name.startswith ( ".fits", -5 ) or
                   self.file_name.startswith ( ".FITS", -5 ) ):
                fits_object = fits ( file_name = self.file_name,
                                     log = self.log )
                fits_object.read ( )
                self.array = fits_object.get_array ( )
                self.cube = cube ( log = self.log,
                                     data = self.array )
                self.metadata = fits_object.get_metadata ( )
                self.update ( )
            elif ( self.file_name.startswith ( ".ad2", -4 ) or
                   self.file_name.startswith ( ".AD2", -4 ) or
                   self.file_name.startswith ( ".ad3", -4 ) or
                   self.file_name.startswith ( ".AD3", -4 ) ):
                adhoc_object = adhoc ( file_name = self.file_name,
                                       log = self.log )
                adhoc_object.read ( )
                self.array = adhoc_object.get_array ( )
                self.cube = cube ( log = self.log,
                                     data = self.array )
        self.log ( "debug: after attempting to read file, " + tuna.io.system.status ( ) )


    def update ( self ):
        if ( self.array == None and
             self.photons == None ):
            self.log ( "debug: Empty Tuna can." )
            self.metadata = None
            self.ndim = None
            self.shape = None
            self.planes = None
            self.rows = None
            self.cols = None
            return

        if ( self.array != None and
             self.photons != None ):
            self.log ( "error: Both self.array and self.photons are populated in update(). Please set one of them to None before calling this method. (Aborting method call)." )
            return

        if ( self.array == None ):
            self.convert_table_into_ndarray ( )
            return

        self.ndim = self.array.ndim
        self.shape = self.array.shape
        self.log ( "debug: can.update: self.array.ndim == %d, self.ndim == %d." % ( self.array.ndim, self.ndim ) )
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
            self.log ( "warning: ndarray has either less than 2 or more than 3 dimensions." )

        self.convert_ndarray_into_table ( )
