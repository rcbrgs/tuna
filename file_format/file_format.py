class file_format ( object ):
    def __init__ ( self, *args, **kwargs ):
        super ( file_format, self ).__init__ ( *args, **kwargs )
        self.__image_ndarray = None

    def get_image_ndarray ( self ):
        return self.__image_ndarray
