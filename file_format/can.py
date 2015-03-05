from .adhoc import adhoc
from .adhoc_ada import ada
from .file_reader import file_reader
from .fits import fits
import numpy

class can ( file_reader ):
    def __init__ ( self, 
                   file_name = None,
                   log = print ):
        super ( can, self ).__init__ ( )
        self.__file_name = file_name
        self.log = log
        self.__metadata = { }
        self.__array = None

    def get_array ( self ):
        return self.__array

    def set_array ( self, array = numpy.ndarray ):
        self.__array = array

    def get_file_name ( self ):
        return self.__file_name

    def set_file_name ( self, file_name = None ):
        self.__file_name = file_name

    def add_metadata ( self, dictionary = { } ):
        for key in dictionary.keys ( ):
            self.__metadata[key] = dictionary[key]

    def get_metadata ( self ):
        return self.__metadata

    def get_metadata_parameter ( self, parameter = str ):
        for entry in self.__metadata:
            if entry['key'] == parameter:
                return entry['value']
        return None

    def read ( self ):
        if self.__file_name:
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):
                ada_object = ada ( file_name = self.__file_name,
                                   log = self.log )
                ada_object.read ( )
                self.__array = ada_object.get_array ( )
                self.__metadata = ada_object.get_metadata ( )
            elif ( self.__file_name.startswith ( ".fits", -5 ) or
                   self.__file_name.startswith ( ".FITS", -5 ) ):
                fits_object = fits ( file_name = self.__file_name,
                                     log = self.log )
                fits_object.read ( )
                self.__array = fits_object.get_array ( )
                self.__metadata = fits_object.get_metadata ( )
            elif ( self.__file_name.startswith ( ".ad2", -4 ) or
                   self.__file_name.startswith ( ".AD2", -4 ) or
                   self.__file_name.startswith ( ".ad3", -4 ) or
                   self.__file_name.startswith ( ".AD3", -4 ) ):
                adhoc_object = adhoc ( file_name = self.__file_name,
                                       log = self.log )
                adhoc_object.read ( )
                self.__array = adhoc_object.get_array ( )

