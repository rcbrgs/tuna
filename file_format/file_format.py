class file_format ( object ):
    def __init__ ( self, *args, **kwargs ):
        super ( file_format, self ).__init__ ( *args, **kwargs )
        self._image_ndarray = None
        self._is_readable = False

    def get_image_ndarray ( self ):
        return self._image_ndarray

    def is_readable ( self ):
        return self._is_readable
