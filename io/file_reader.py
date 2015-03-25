class file_reader ( object ):
    def __init__ ( self, *args, **kwargs ):
        super ( file_reader, self ).__init__ ( *args, **kwargs )
        self._image_ndarray = None
        self._is_readable = False

    def get_image_ndarray ( self ):
        print ( "In file_reader::get_image_ndarray" )
        return self._image_ndarray

    def is_readable ( self ):
        return self._is_readable
