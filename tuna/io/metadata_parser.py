"""This module's scope covers the operations related to metadata.
"""
__version__ = "0.1.1"
__changelog = {
    "0.1.1": {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    "0.1.0": {"Tuna": "0.14.0", "Change": "updated docstrings to new style."},
}

import logging
import re
import sys

class MetadataParser(object):
    """Responsible for translating metadata from ADHOC's ADT to Tuna's internal
    representation.

    Its constructor signature is:

    Parameters:

    * file_name : string : defaults to None
        Full or relative path and file name for an ADT file.
    """
    def __init__(self, file_name = None):
        super(MetadataParser, self).__init__()
        self.log = logging.getLogger(__name__)

        self.__file_name = file_name
        self.__results = {}
        if self.__file_name != None:
            self.run()

    def get_metadata(self):
        """Access the parsed metadata.

        Returns:

        * self.__results : dictionary
            Contains the metadata obtained from reading the input file.
        """
        return self.__results

    def run(self):
        """Verify file format and attempts to parse the metadata accordingly.
        """
        self.log.debug("%s %s" % (sys._getframe().f_code.co_name,
                                  sys._getframe().f_code.co_varnames))

        if self.__file_name != None:
            if (self.__file_name.startswith(".ADT", -4) or
                self.__file_name.startswith(".adt", -4)):
                self.read_adt_metadata()
        else:
            self.log("File name %s does not have .ADT or .adt suffix, " \
                     + "aborting." % ( self.__file_name ) )

def get_metadata(file_name = None):
    """Conveniently return the metadata, given a file name.

    Parameters:

    * file_name : string
        Containing a valid file name (and optionally, an absolute or relative 
        path).

    Returns:

    * parser.get_metadata ( ) : dictionary
        Contains the metadata obtained from reading file_name.
    """
    log = logging.getLogger(__name__)
    log.debug("%s %s" % (sys._getframe().f_code.co_name,
                         sys._getframe().f_code.co_varnames))

    if file_name:
        parser = metadata_parser(file_name = file_name)
        return parser.get_metadata()
