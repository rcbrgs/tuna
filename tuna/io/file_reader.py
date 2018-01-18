"""
This module's scope covers abstractions related to file format readers.
"""

import logging
import sys

class file_reader ( object ):
    """
    This class is responsible for abstracting common features of the file readers in a single code artifact.

    It is not meant to be user-serviceable.
    """
    def __init__ ( self, *args, **kwargs ):
        super ( file_reader, self ).__init__ ( *args, **kwargs )
        self.__version__ = "0.1.0"
        self.changelog = {
            "0.1.0" : "Tuna 0.13.0 : improved documentation."
            }
        self.log = logging.getLogger ( __name__ )

        self._image_ndarray = None
        self._is_readable = False

    def get_image_ndarray ( self ):
        """
        This method's goal is to offer access to the array containing the image data.

        Returns:

        * self._image_ndarray : numpy.ndarray : defaults to None
            Contains the current data for this reader. This should be set by derived classes.
        """
        self.log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                                     sys._getframe ( ).f_code.co_varnames ) )

        return self._image_ndarray

    def is_readable ( self ):
        """
        This method's goal is to check if the input file is readable.

        Returns:

        * self._is_readable : bool : defaults to False
            True if the file is readable; should be set by derived classes.
        """
        return self._is_readable
