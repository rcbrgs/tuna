import logging
import re

class metadata_parser ( object ):
    """
    Responsible for translating metadata from any file format (but supports only ADT at the moment) to Tuna's internal representation.
    """
    def __init__ ( self, file_name = None ):
        super ( metadata_parser, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )

        self.__file_name = file_name
        self.__results = { }
        if self.__file_name != None:
            self.run ( )

    def get_metadata ( self ):
        """
        Returns self.__results
        """
        return self.__results

    def run ( self ):
        """
        Verifies file format and attempts to parse the metadata accordingly.
        """
        self.log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                                     sys._getframe ( ).f_code.co_varnames ) )

        if self.__file_name != None:
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):
                self.read_adt_metadata ( )
        else:
            self.log ( "File name %s does not have .ADT or .adt suffix, aborting." % ( self.__file_name ) )

def get_metadata ( file_name = None ):
    """
    Convenience function that returns the metadata, given a file name.

    Parameters:

    - file_name: a string containing a valid file name (and optionally, an absolute or relative path).
    """
    log = logging.getLogger ( __name__ )
    log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                            sys._getframe ( ).f_code.co_varnames ) )

    if file_name:
        parser = metadata_parser ( file_name = file_name )
        return parser.get_metadata ( )
