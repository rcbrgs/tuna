import logging

class file_reader ( object ):
    def __init__ ( self, *args, **kwargs ):
        super ( file_reader, self ).__init__ ( *args, **kwargs )
        self.log = logging.getLogger ( __name__ )

        self._image_ndarray = None
        self._is_readable = False

    def get_image_ndarray ( self ):
        self.log.debug ( "%s %s" % ( sys._getframe ( ).f_code.co_name,
                                     sys._getframe ( ).f_code.co_varnames ) )

        return self._image_ndarray

    def is_readable ( self ):
        return self._is_readable
