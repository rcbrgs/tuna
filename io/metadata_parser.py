import re

class metadata_parser ( object ):
    def __init__ ( self, file_name = None, log = print ):
        super ( metadata_parser, self ).__init__ ( )
        self.log = log
        self.__file_name = file_name
        self.__results = { }
        if self.__file_name != None:
            self.run ( )

    def get_metadata ( self ):
        return self.__results

    def run ( self ):
        if self.__file_name != None:
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):
                self.read_adt_metadata ( )
        else:
            self.log ( "File name %s does not have .ADT or .adt suffix, aborting." % ( self.__file_name ) )

def get_metadata ( file_name = None ):
    if file_name:
        parser = metadata_parser ( file_name = file_name )
        return parser.get_metadata ( )
