from .adhoc import adhoc
from .adhoc_ada import ada
from tuna.data_cube.cube import cube
from .file_reader import file_reader
from .fits import fits
import numpy

class can ( file_reader ):
    def __init__ ( self, 
                   file_name = None,
                   log = print ):
        super ( can, self ).__init__ ( )
        self.array = None
        self.o_cube = None
        self.__file_name = file_name
        self.log = log
        self.metadata = { }

        self.__d_photons = None

    def __add__ ( self,
                  o_can ):
        o_result = can ( log = self.log )
        o_result.o_cube = self.o_cube + o_can.o_cube
        o_result.array = o_result.o_cube.get_array ( )

        return o_result

    def get_file_name ( self ):
        return self.__file_name

    def set_file_name ( self, file_name = None ):
        self.__file_name = file_name

    def add_metadata ( self, dictionary = { } ):
        for key in dictionary.keys ( ):
            self.metadata[key] = dictionary[key]

    def get_photons ( self ):
        return self.__d_photons

    def read ( self ):
        if self.__file_name:
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):
                ada_object = ada ( file_name = self.__file_name,
                                   log = self.log )
                ada_object.read ( )
                self.array = ada_object.get_array ( )
                self.o_cube = cube ( log = self.log,
                                     tan_data = self.array )
                self.metadata = ada_object.get_metadata ( )
                self.__d_photons = ada_object.get_photons ( )
            elif ( self.__file_name.startswith ( ".fits", -5 ) or
                   self.__file_name.startswith ( ".FITS", -5 ) ):
                fits_object = fits ( file_name = self.__file_name,
                                     log = self.log )
                fits_object.read ( )
                self.array = fits_object.get_array ( )
                self.o_cube = cube ( log = self.log,
                                     tan_data = self.array )
                self.metadata = fits_object.get_metadata ( )
            elif ( self.__file_name.startswith ( ".ad2", -4 ) or
                   self.__file_name.startswith ( ".AD2", -4 ) or
                   self.__file_name.startswith ( ".ad3", -4 ) or
                   self.__file_name.startswith ( ".AD3", -4 ) ):
                adhoc_object = adhoc ( file_name = self.__file_name,
                                       log = self.log )
                adhoc_object.read ( )
                self.array = adhoc_object.get_array ( )
                self.o_cube = cube ( log = self.log,
                                     tan_data = self.array )
