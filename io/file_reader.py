import logging

class file_reader ( object ):
    """
    Class where commonalities between the multiple file formats can be reused.
    """
    def __init__ ( self, *args, **kwargs ):
        super ( file_reader, self ).__init__ ( *args, **kwargs )
        self.log = logging.getLogger ( __name__ )

        self._image_ndarray = None
        self._is_readable = False

    def get_image_ndarray ( self ):
        """
        Return the array containing the image data.
        """
        self.log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                                     sys._getframe ( ).f_code.co_varnames ) )

        return self._image_ndarray

    def is_readable ( self ):
        """
        Returns True if the specified file is readable.
        """
        return self._is_readable
